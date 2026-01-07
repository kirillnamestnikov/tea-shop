from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Category, Product


class ShopModelTests(TestCase):
    """Тесты моделей магазина"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            slug='smartphone',
            price=Decimal('699.99'),
            available=True
        )

    def test_category_creation(self):
        """Создание категории"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')

    def test_product_creation(self):
        """Создание продукта"""
        self.assertEqual(self.product.name, 'Smartphone')
        self.assertEqual(self.product.category, self.category)
        self.assertTrue(self.product.available)

    def test_category_get_absolute_url(self):
        """URL категории"""
        url = self.category.get_absolute_url()
        expected_url = reverse('shop:product_list_by_category',
                               args=[self.category.slug])
        self.assertEqual(url, expected_url)

    def test_product_get_absolute_url(self):
        """URL продукта"""
        url = self.product.get_absolute_url()
        expected_url = reverse('shop:product_detail',
                               args=[self.product.id, self.product.slug])
        self.assertEqual(url, expected_url)


class ShopViewTests(TestCase):
    """Тесты views магазина"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            slug='smartphone',
            price=Decimal('699.99'),
            available=True
        )

    def test_product_list_view(self):
        """Список продуктов"""
        response = self.client.get(reverse('shop:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/list.html')
        self.assertIn('products', response.context)

    def test_product_detail_view(self):
        """Детали продукта"""
        response = self.client.get(
            reverse('shop:product_detail',
                    args=[self.product.id, self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/detail.html')
        self.assertEqual(response.context['product'], self.product)
