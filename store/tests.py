import os
import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from shopease.settings import _build_host_security_settings
from store.models import CartItem, Category, Order, OrderItem, Product, ProductVariant, SubCategory


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


class PublicSecurityTests(TestCase):
    def test_login_rejects_external_next_redirects(self):
        user = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='secret123',
        )

        response = self.client.post(
            reverse('login'),
            {
                'email': user.email,
                'password': 'secret123',
                'next': 'https://evil.example/phish',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_public_products_api_is_read_only(self):
        response = self.client.post(reverse('product-list'), {})

        self.assertEqual(response.status_code, 405)


class AdminProductUpdateTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='secret123',
            is_staff=True,
        )
        self.category, _ = Category.objects.get_or_create(category_name='mens')
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


class RazorpayFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='secret123',
        )
        self.category, _ = Category.objects.get_or_create(category_name='mens')
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            subcategory_name='shirts',
        )
        self.product = Product.objects.create(
            product_name='Live Payment Shirt',
            brand='ShopEase',
            category=self.category,
            subcategory=self.subcategory,
            sku='LIVE-PAYMENT-SHIRT-1',
            price=Decimal('1000.00'),
            discount_percent=Decimal('10.00'),
            description='For Razorpay flow tests',
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            quantity=6,
            image1='men_shirt_black_front.jpg',
        )

    def _create_pending_order(self):
        order = Order.objects.create(
            user=self.user,
            full_name='Buyer Example',
            phone_number='9999999999',
            email='buyer@example.com',
            address='123 Test Street',
            city='Chennai',
            state='Tamil Nadu',
            pincode='600001',
            country='India',
            payment_method='Razorpay',
            payment_status='Created',
            currency='INR',
            subtotal=Decimal('1800.00'),
            total_items=2,
            status='Pending Payment',
            razorpay_order_id='order_live_123',
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            selected_size='M',
            quantity=2,
            unit_price=Decimal('900.00'),
            line_total=Decimal('1800.00'),
        )
        return order

    @override_settings(
        RAZORPAY_MODE='test',
        RAZORPAY_KEY_ID='rzp_test_example',
        RAZORPAY_KEY_SECRET='test_secret',
    )
    @patch('store.views._create_razorpay_order')
    def test_standard_checkout_creates_order_using_cart_total(self, mock_create_razorpay_order):
        mock_create_razorpay_order.return_value = {
            'id': 'order_live_123',
            'currency': 'INR',
        }
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            selected_size='M',
            quantity=2,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('create_razorpay_checkout'),
            {
                'full_name': 'Buyer Example',
                'phone_number': '9999999999',
                'email': 'buyer@example.com',
                'address': '123 Test Street',
                'city': 'Chennai',
                'state': 'Tamil Nadu',
                'pincode': '600001',
                'country': 'India',
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['amount'], 180000)
        self.assertEqual(payload['razorpay_order_id'], 'order_live_123')

        order = Order.objects.get(order_id=payload['local_order_id'])
        self.assertEqual(order.subtotal, Decimal('1800.00'))
        self.assertEqual(order.total_items, 2)
        self.assertEqual(order.payment_status, 'Created')
        self.assertEqual(order.razorpay_order_id, 'order_live_123')

    @override_settings(
        RAZORPAY_MODE='test',
        RAZORPAY_KEY_ID='rzp_test_example',
        RAZORPAY_KEY_SECRET='test_secret',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@example.com',
    )
    @patch('store.views._verify_razorpay_signature', return_value=True)
    @patch('store.views._fetch_razorpay_payment')
    def test_verify_payment_uses_saved_order_total_and_confirms_order(self, mock_fetch_razorpay_payment, mock_verify_signature):
        order = self._create_pending_order()
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            selected_size='M',
            quantity=2,
        )
        mock_fetch_razorpay_payment.return_value = {
            'status': 'captured',
            'amount': 180000,
            'order_id': 'order_live_123',
            'currency': 'INR',
        }
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('verify_razorpay_payment'),
            {
                'local_order_id': order.order_id,
                'razorpay_order_id': 'order_live_123',
                'razorpay_payment_id': 'pay_live_123',
                'razorpay_signature': 'signature_123',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order_success', kwargs={'order_id': order.order_id}))

        order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(order.payment_status, 'Captured')
        self.assertEqual(order.payment_method, 'Razorpay')
        self.assertEqual(order.razorpay_payment_id, 'pay_live_123')
        self.assertEqual(order.status, 'Placed')
        self.assertEqual(self.variant.quantity, 4)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        mock_verify_signature.assert_called_once()

    @override_settings(
        RAZORPAY_WEBHOOK_SECRET='webhook_test_secret',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@example.com',
    )
    def test_webhook_marks_captured_order_paid(self):
        order = self._create_pending_order()
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            selected_size='M',
            quantity=2,
        )
        payload = {
            'event': 'order.paid',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_live_123',
                        'amount': 180000,
                        'currency': 'INR',
                        'status': 'captured',
                        'order_id': 'order_live_123',
                    },
                },
                'order': {
                    'entity': {
                        'id': 'order_live_123',
                        'amount_paid': 180000,
                        'currency': 'INR',
                        'status': 'paid',
                    },
                },
            },
        }
        raw_body = json.dumps(payload).encode('utf-8')
        signature = hmac.new(
            b'webhook_test_secret',
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        response = self.client.post(
            reverse('razorpay_webhook'),
            data=raw_body,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=signature,
            HTTP_X_RAZORPAY_EVENT_ID='event_123',
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(order.payment_status, 'Paid')
        self.assertEqual(order.razorpay_payment_id, 'pay_live_123')
        self.assertEqual(order.status, 'Placed')
        self.assertEqual(self.variant.quantity, 4)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    @override_settings(
        RAZORPAY_MODE='test',
        RAZORPAY_KEY_ID='rzp_test_example',
        RAZORPAY_KEY_SECRET='test_secret',
    )
    @patch('store.views._fetch_razorpay_payment_link')
    def test_payment_link_callback_rejects_wrong_logged_in_user_before_finalizing(self, mock_fetch_payment_link):
        owner = self.user
        stranger = User.objects.create_user(
            username='intruder@example.com',
            email='intruder@example.com',
            password='secret123',
        )
        order = Order.objects.create(
            user=owner,
            full_name='Buyer Example',
            phone_number='9999999999',
            email='buyer@example.com',
            address='123 Test Street',
            city='Chennai',
            state='Tamil Nadu',
            pincode='600001',
            country='India',
            payment_method='Razorpay Payment Link',
            payment_status='Created',
            currency='INR',
            subtotal=Decimal('1800.00'),
            total_items=2,
            status='Pending Payment',
            razorpay_order_id='plink_live_123',
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            selected_size='M',
            quantity=2,
            unit_price=Decimal('900.00'),
            line_total=Decimal('1800.00'),
        )
        mock_fetch_payment_link.return_value = {
            'status': 'paid',
            'amount_paid': 180000,
            'currency': 'INR',
            'reference_id': f'shopease_{order.order_id}',
            'payments': [{'payment_id': 'pay_live_123'}],
        }
        self.client.force_login(stranger)

        signature_payload = f'plink_live_123|shopease_{order.order_id}|paid|pay_live_123'
        signature = hmac.new(
            b'test_secret',
            signature_payload.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

        response = self.client.get(
            reverse('razorpay_payment_link_callback'),
            {
                'local_order_id': order.order_id,
                'razorpay_payment_link_id': 'plink_live_123',
                'razorpay_payment_link_reference_id': f'shopease_{order.order_id}',
                'razorpay_payment_link_status': 'paid',
                'razorpay_payment_id': 'pay_live_123',
                'razorpay_signature': signature,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(order.payment_status, 'Created')
        self.assertEqual(order.status, 'Pending Payment')
        self.assertEqual(self.variant.quantity, 6)
