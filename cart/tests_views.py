from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from shop.models import Product, Category


class CartViewTests(TestCase):
    """Тесты views корзины с использованием Django Client"""

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

    def test_cart_add_post(self):
        """Добавление товара через POST запрос"""
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '2', 'override': False}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))

        session = self.client.session
        self.assertIn('cart', session)
        cart_data = session['cart']

        product_id = str(self.product.id)
        self.assertIn(product_id, cart_data)
        self.assertEqual(cart_data[product_id]['quantity'], 2)

    def test_cart_detail_get(self):
        """GET запрос на просмотр корзины"""
        response = self.client.get(reverse('cart:cart_detail'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('cart', response.context)

    def test_cart_remove_post(self):
        """Удаление товара из корзины"""
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '2', 'override': False}
        )

        response = self.client.post(
            reverse('cart:cart_remove', args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))
        session = self.client.session
        cart_data = session.get('cart', {})
        self.assertEqual(cart_data, {})

    def test_cart_add_with_override(self):
        """Добавление с перезаписью количества"""
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '2', 'override': False}
        )
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '5', 'override': True}
        )

        session = self.client.session
        cart_data = session['cart']
        product_id = str(self.product.id)
        self.assertEqual(cart_data[product_id]['quantity'], 5)

    def test_cart_add_invalid_form(self):
        """Добавление с невалидной формой"""
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '15'}
        )
        self.assertEqual(response.status_code, 302)

    def test_cart_remove_nonexistent_product(self):
        """Удаление несуществующего товара"""
        response = self.client.post(
            reverse('cart:cart_remove', args=[999])
        )
        self.assertEqual(response.status_code, 404)
