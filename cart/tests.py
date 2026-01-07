from decimal import Decimal
from unittest.mock import Mock
from django.test import TestCase
from django.conf import settings
from shop.models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm


class CartTests(TestCase):
    """Базовые тесты корзины"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            available=True
        )

        self.mock_session = {}
        self.mock_request = Mock()
        self.mock_request.session = self.mock_session
        self.cart = Cart(self.mock_request)

    def test_cart_initialization(self):
        """Инициализация корзины"""
        self.assertEqual(self.cart.cart, {})

    def test_cart_initialization_with_existing_session(self):
        """Инициализация корзины с существующей сессией"""
        mock_session = {'cart': {str(self.product.id): {'quantity': 2, 'price': '100.00'}}}
        mock_request = Mock()
        mock_request.session = mock_session

        cart = Cart(mock_request)
        self.assertEqual(len(cart.cart), 1)
        self.assertEqual(cart.cart[str(self.product.id)]['quantity'], 2)

    def test_add_product(self):
        """Добавление товара в корзину"""
        self.cart.save = Mock()
        self.cart.add(self.product, quantity=2)
        product_id = str(self.product.id)
        self.assertIn(product_id, self.cart.cart)
        self.assertEqual(self.cart.cart[product_id]['quantity'], 2)
        self.assertEqual(self.cart.cart[product_id]['price'], '100.00')
        self.cart.save.assert_called_once()

    def test_add_product_with_override(self):
        """Добавление товара с перезаписью количества"""
        self.cart.save = Mock()
        self.cart.add(self.product, quantity=2)
        self.cart.add(self.product, quantity=5, override_quantity=True)
        product_id = str(self.product.id)
        self.assertEqual(self.cart.cart[product_id]['quantity'], 5)

    def test_remove_product(self):
        """Удаление товара из корзины"""
        self.cart.save = Mock()

        self.cart.add(self.product, quantity=1)
        self.cart.save.reset_mock()

        self.cart.remove(self.product)

        product_id = str(self.product.id)
        self.assertNotIn(product_id, self.cart.cart)
        self.cart.save.assert_called_once()

    def test_remove_nonexistent_product(self):
        """Удаление несуществующего товара"""
        self.cart.save = Mock()

        self.cart.remove(self.product)
        self.cart.save.assert_not_called()

    def test_total_price(self):
        """Подсчет общей суммы"""
        self.cart.save = Mock()

        self.cart.add(self.product, quantity=3)
        total = self.cart.get_total_price()

        self.assertEqual(total, Decimal('300.00'))

    def test_cart_length(self):
        """Количество товаров в корзине"""
        self.cart.save = Mock()

        self.assertEqual(len(self.cart), 0)

        self.cart.add(self.product, quantity=3)
        self.assertEqual(len(self.cart), 3)

    def test_clear_cart(self):
        """Очистка корзины"""
        self.cart.save = Mock()

        self.cart.add(self.product, quantity=2)
        self.cart.save.reset_mock()

        self.cart.clear()

        self.assertNotIn(settings.CART_SESSION_ID, self.mock_session)
        self.cart.save.assert_called_once()

    def test_cart_iteration(self):
        """Итерация по корзине"""
        self.cart.save = Mock()

        self.cart.add(self.product, quantity=2)

        items = list(self.cart)
        self.assertEqual(len(items), 1)
        if items:
            item = items[0]
            self.assertEqual(item['product'], self.product)
            self.assertEqual(item['quantity'], 2)
            self.assertEqual(item['price'], Decimal('100.00'))
            self.assertEqual(item['total_price'], Decimal('200.00'))

    def test_get_total_price_empty(self):
        """Общая сумма пустой корзины"""
        total = self.cart.get_total_price()
        self.assertEqual(total, Decimal('0.00'))


class CartFormTests(TestCase):
    """Тесты формы добавления в корзину"""

    def test_valid_form(self):
        """Валидная форма"""
        form_data = {'quantity': '2', 'override': False}
        form = CartAddProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['quantity'], 2)

    def test_invalid_form_quantity_too_high(self):
        """Невалидное количество (больше 10)"""
        form_data = {'quantity': '15', 'override': False}
        form = CartAddProductForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_form_choices_range(self):
        """Диапазон выбора количества"""
        form = CartAddProductForm()
        choices = form.fields['quantity'].choices

        self.assertEqual(len(choices), 10)
        for i in range(1, 11):
            self.assertIn((i, str(i)), choices)
