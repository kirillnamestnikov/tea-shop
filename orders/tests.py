from decimal import Decimal
from django.test import TestCase
from shop.models import Product, Category
from .models import Order, OrderItem
from .forms import OrderCreateForm


class OrderModelTests(TestCase):
    """Тесты моделей заказов"""

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

        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='New York'
        )

    def test_order_creation(self):
        """Создание заказа"""
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.last_name, 'Doe')
        self.assertEqual(self.order.email, 'john@example.com')
        self.assertEqual(self.order.address, '123 Main St')
        self.assertEqual(self.order.postal_code, '12345')
        self.assertEqual(self.order.city, 'New York')
        self.assertFalse(self.order.paid)
        self.assertIsNotNone(self.order.created)
        self.assertIsNotNone(self.order.updated)

    def test_order_str_method(self):
        """Строковое представление заказа"""
        self.assertEqual(str(self.order), f'Order {self.order.id}')

    def test_order_item_creation(self):
        """Создание элемента заказа"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('100.00'),
            quantity=2
        )

        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.price, Decimal('100.00'))
        self.assertEqual(order_item.quantity, 2)

    def test_order_item_get_cost(self):
        """Расчет стоимости элемента заказа"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('150.00'),
            quantity=3
        )

        expected_cost = Decimal('150.00') * 3
        self.assertEqual(order_item.get_cost(), expected_cost)

    def test_order_total_cost(self):
        """Подсчет общей стоимости заказа"""
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('100.00'),
            quantity=2
        )
        product2 = Product.objects.create(
            category=self.category,
            name='Product 2',
            slug='product-2',
            price=Decimal('200.00'),
            available=True
        )

        OrderItem.objects.create(
            order=self.order,
            product=product2,
            price=Decimal('200.00'),
            quantity=1
        )

        expected_total = (Decimal('100.00') * 2) + Decimal('200.00')
        self.assertEqual(self.order.get_total_cost(), expected_total)

    def test_order_total_cost_empty(self):
        """Общая стоимость пустого заказа"""
        self.assertEqual(self.order.get_total_cost(), Decimal('0.00'))

    def test_order_ordering(self):
        """Проверка сортировки заказов"""
        order2 = Order.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            address='456 Oak St',
            postal_code='67890',
            city='Los Angeles'
        )

        orders = Order.objects.all()
        self.assertEqual(orders[0], order2)
        self.assertEqual(orders[1], self.order)


class OrderFormTests(TestCase):
    """Тесты формы создания заказа"""
    def test_valid_order_form(self):
        """Валидная форма заказа"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        form = OrderCreateForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        order = form.save()
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.last_name, 'Doe')
        self.assertEqual(order.email, 'john@example.com')
        self.assertEqual(order.address, '123 Main St')
        self.assertEqual(order.postal_code, '12345')
        self.assertEqual(order.city, 'New York')
        self.assertFalse(order.paid)  # По умолчанию False

    def test_invalid_order_form_missing_email(self):
        """Невалидная форма (отсутствует email)"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': '',  # Пустой email
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_order_form_missing_first_name(self):
        """Невалидная форма (отсутствует имя)"""
        form_data = {
            'first_name': '',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_invalid_order_form_invalid_email(self):
        """Невалидная форма (неправильный email)"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'not-an-email',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_order_form_fields(self):
        """Проверка полей формы"""
        form = OrderCreateForm()

        expected_fields = [
            'first_name', 'last_name', 'email',
            'address', 'postal_code', 'city'
        ]

        self.assertEqual(list(form.fields.keys()), expected_fields)
