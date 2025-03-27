from rest_framework import serializers
from .models import Product, CartItem, Cart, CouponCode, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['user', 'items', 'total_amount']  # Removed 'coupon_code'

class CouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponCode
        fields = ['code', 'is_used', 'order_n', 'discount_percentage']  # Added 'discount_percentage'

class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer()
    discount_code = CouponCodeSerializer()

    class Meta:
        model = Order
        fields = ['user', 'cart', 'discount_code', 'total_amount', 'created_at', 'order_number']  # Added 'created_at' and 'order_number'
