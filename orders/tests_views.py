from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from shop.models import Product, Category
from orders.models import Order, OrderItem


class OrderViewTests(TestCase):

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

    def test_order_create_get(self):
        """GET запрос на создание заказа"""
        response = self.client.get(reverse('orders:order_create'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_order_create_post(self):
        """POST запрос на создание заказа"""
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '2', 'override': False}
        )

        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        response = self.client.post(
            reverse('orders:order_create'),
            data=form_data
        )

        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.first_name, 'John')

        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)

        item = OrderItem.objects.filter(order=order).first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, Decimal('100.00'))

    def test_order_create_invalid_form(self):
        """POST запрос с невалидными данными"""
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': '1', 'override': False}
        )

        invalid_data = {
            'first_name': '',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }

        response = self.client.post(
            reverse('orders:order_create'),
            data=invalid_data
        )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_order_create_empty_cart(self):
        """Создание заказа без товаров в корзине"""
        form_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'address': '456 Oak St',
            'postal_code': '67890',
            'city': 'Los Angeles'
        }

        response = self.client.post(
            reverse('orders:order_create'),
            data=form_data
        )

        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.first_name, 'Jane')

        self.assertEqual(order.items.count(), 0)
