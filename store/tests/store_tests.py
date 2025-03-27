from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem

class CartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name="Test Product", price=100.00)

    def test_add_to_cart(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post('/cart/add_item/', {'product_id': self.product.id, 'quantity': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.get(user=self.user).total_amount, 200.00)
