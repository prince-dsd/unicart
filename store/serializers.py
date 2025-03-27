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
        fields = ['user', 'items', 'total_amount']

class CouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponCode
        fields = ['code', 'discount_percentage', 'is_used', 'order_n']

class OrderSerializer(serializers.ModelSerializer):
    discount_code = CouponCodeSerializer()  # Serialize the discount code
    total_items_purchased = serializers.IntegerField()  # Include total items purchased
    total_discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # Include total discount amount

    class Meta:
        model = Order
        fields = [
            'user',
            'discount_code',
            'total_amount',
            'total_discount_amount',
            'total_items_purchased',
            'created_at',
            'order_number'
        ]
