import os
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from shopease.settings import _build_host_security_settings
from store.models import Category, Product, ProductVariant, SubCategory


class PublicPolicyPagesTests(TestCase):
    def test_policy_pages_render(self):
        cases = [
            ('privacy_policy', 'Privacy Policy'),
            ('refund_policy', 'Refund and Cancellation Policy'),
            ('terms_and_conditions', 'Terms and Conditions'),
        ]

        for route_name, expected_text in cases:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)

    def test_home_footer_exposes_customer_policy_links(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('privacy_policy'))
        self.assertContains(response, reverse('refund_policy'))
        self.assertContains(response, reverse('terms_and_conditions'))


class HostSecuritySettingsTests(TestCase):
    def test_payment_callback_domain_is_added_to_allowed_hosts_and_csrf_origins(self):
        with patch.dict(os.environ, {
            'ALLOWED_HOSTS': '127.0.0.1,localhost',
            'CSRF_TRUSTED_ORIGINS': 'https://existing.example.com',
            'PAYMENT_CALLBACK_BASE_URL': 'https://shop.example.com/payments',
        }, clear=False):
            allowed_hosts, trusted_origins = _build_host_security_settings()

        self.assertIn('shop.example.com', allowed_hosts)
        self.assertIn('https://shop.example.com', trusted_origins)
        self.assertIn('https://existing.example.com', trusted_origins)


class AdminProductUpdateTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='secret123',
            is_staff=True,
        )
        self.category = Category.objects.create(category_name='mens')
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            subcategory_name='shirts',
        )
        self.product = Product.objects.create(
            product_name='Office Shirt',
            brand='ShopEase',
            category=self.category,
            subcategory=self.subcategory,
            sku='OFFICE-SHIRT-1',
            price=Decimal('1000.00'),
            discount_percent=Decimal('10.00'),
            description='Before update',
            is_active=True,
        )
        ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            quantity=5,
            image1='men_shirt_black_front.jpg',
        )

    def test_product_save_recalculates_offer_price(self):
        self.product.price = Decimal('1200.00')
        self.product.discount_percent = Decimal('25.00')
        self.product.save()
        self.product.refresh_from_db()

        self.assertEqual(self.product.offer_price, Decimal('900.00'))

    def test_admin_edit_updates_storefront_values(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse('admin_product_edit', args=[self.product.product_id]),
            {
                'product_name': 'Office Shirt Updated',
                'brand': 'ShopEase Pro',
                'category_id': self.category.category_id,
                'subcategory_id': self.subcategory.subcategory_id,
                'sku': self.product.sku,
                'price': '1500.00',
                'discount_percent': '20.00',
                'description': 'Updated from admin',
                'size': 'L',
                'quantity': '9',
                'color': 'Black',
                'image1': 'men_shirt_black_front.jpg',
                'image2': '',
                'image3': '',
                'image4': '',
                'is_active': 'on',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        variant = ProductVariant.objects.get(product=self.product)

        self.assertEqual(self.product.product_name, 'Office Shirt Updated')
        self.assertEqual(self.product.brand, 'ShopEase Pro')
        self.assertEqual(self.product.offer_price, Decimal('1200.00'))
        self.assertEqual(variant.size, 'L')
        self.assertEqual(variant.quantity, 9)

        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, 'Office Shirt Updated')
        self.assertContains(home_response, 'Rs. 1200.00')
