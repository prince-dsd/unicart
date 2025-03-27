from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Product, Cart, CartItem, CouponCode, Order


class CartViewSetTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword')

        # Create test products
        self.product1 = Product.objects.create(name="Product 1", price=100.00)
        self.product2 = Product.objects.create(name="Product 2", price=200.00)

        # Create a test coupon code
        self.coupon = CouponCode.objects.create(code="DISCOUNT10", discount_percentage=10.00, is_used=False)

        # Set up API client
        self.client = APIClient()

    def test_add_items_to_cart(self):
        """Test adding multiple items to the cart."""
        self.client.login(username='testuser', password='password')
        response = self.client.post('/api/cart/add-items/', {
            'products': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        })
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_amount, 400.00)
        self.assertEqual(cart.items.count(), 2)

    def test_checkout_cart_with_coupon(self):
        """Test checking out the cart with a valid coupon code."""
        self.client.login(username='testuser', password='password')

        # Add items to the cart
        self.client.post('/api/cart/add-items/', {
            'products': [{'product_id': self.product1.id, 'quantity': 2}]
        })

        # Checkout with a valid coupon code
        response = self.client.post('/api/cart/checkout/', {'coupon_code': 'DISCOUNT10'})
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_amount, 180.00)  # 10% discount applied
        self.assertEqual(order.total_items_purchased, 2)

    def test_checkout_cart_without_coupon(self):
        """Test checking out the cart without a coupon code."""
        self.client.login(username='testuser', password='password')

        # Add items to the cart
        self.client.post('/api/cart/add-items/', {
            'products': [{'product_id': self.product1.id, 'quantity': 1}]
        })

        # Checkout without a coupon code
        response = self.client.post('/api/cart/checkout/', {})
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_amount, 100.00)  # No discount applied
        self.assertEqual(order.total_items_purchased, 1)

    def test_generate_discount_code(self):
        """Test generating a discount code (admin only)."""
        self.client.login(username='admin', password='adminpassword')

        # Generate a discount code for the 5th order
        response = self.client.post('/api/cart/generate-discount-code/', {'nth_order': 5})
        self.assertEqual(response.status_code, 201)
        self.assertIn('coupon_code', response.data)

    def test_generate_discount_code_non_admin(self):
        """Test that non-admin users cannot generate discount codes."""
        self.client.login(username='testuser', password='password')

        # Attempt to generate a discount code
        response = self.client.post('/api/cart/generate-discount-code/', {'nth_order': 5})
        self.assertEqual(response.status_code, 403)

    def test_unused_coupons(self):
        """Test retrieving unused coupon codes."""
        self.client.login(username='testuser', password='password')

        # Retrieve unused coupons
        response = self.client.get('/api/cart/unused-coupons/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'DISCOUNT10')

    def test_report_api(self):
        """Test generating a sales report (admin only)."""
        self.client.login(username='admin', password='adminpassword')

        # Add items to the cart and checkout
        self.client.post('/api/cart/add-items/', {
            'products': [{'product_id': self.product1.id, 'quantity': 1}]
        })
        self.client.post('/api/cart/checkout/', {})

        # Generate the report
        response = self.client.get('/api/cart/report/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders', response.data)
        self.assertIn('summary', response.data)
