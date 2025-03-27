from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal
from .models import Cart, Product, CouponCode, CartItem, Order
from .serializers import CartSerializer, OrderSerializer
from .swagger import cart_add_item, cart_checkout, generate_discount_code, report

class CartViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(**cart_add_item)
    @action(detail=False, methods=['post'], url_path='add-item')  # Changed url_path
    def add_item(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(quantity, int) or quantity < 1:
            return Response(
                {"error": "Quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=user)
            
            # Ensure CartItem is tied to the user's cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,  # Associate the CartItem with the user's cart
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Recalculate total amount
            cart.total_amount = sum(
                item.product.price * item.quantity 
                for item in cart.items.all()
            )
            cart.save()

            return Response(CartSerializer(cart).data)
            
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(**cart_checkout)
    @action(detail=False, methods=['post'], url_path='checkout')  # Changed detail to False
    def checkout(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                return Response(
                    {"error": "Cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            coupon_code = request.data.get('coupon_code')
            discount_code = None
            discount_amount = 0

            if coupon_code:
                try:
                    discount_code = CouponCode.objects.get(code=coupon_code, is_used=False)
                    discount_amount = cart.total_amount * (discount_code.discount_percentage / 100)
                    cart.total_amount -= discount_amount
                    discount_code.is_used = True
                    discount_code.save()
                except CouponCode.DoesNotExist:
                    return Response(
                        {"error": "Invalid or used coupon code"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create order
            order = Order.objects.create(
                user=user,
                cart=cart,
                discount_code=discount_code,
                total_amount=cart.total_amount
            )

            # Generate discount code for every nth order (e.g., every 5th order)
            nth_order = 5  # Change this to your desired nth number
            if order.order_number % nth_order == 0:
                new_code = f'DISCOUNT-{order.order_number}'
                CouponCode.objects.create(
                    code=new_code,
                    order_n=order.order_number,
                    discount_percentage=10.0  # Default discount percentage
                )

            # Clear cart
            cart.items.clear()
            cart.total_amount = 0
            cart.save()

            return Response({
                'order': OrderSerializer(order).data,
                'message': f'Order #{order.order_number} created successfully'
            }, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(**generate_discount_code)
    @action(detail=False, methods=['post'], url_path='generate-discount-code')
    def generate_discount_code(self, request):
        """Admin API to manually generate discount codes"""
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )

        nth_order = request.data.get('nth_order')

        if not isinstance(nth_order, int) or nth_order < 1:
            return Response(
                {"error": "nth_order must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = f'DISCOUNT-{nth_order}'
        if CouponCode.objects.filter(code=code).exists():
            return Response(
                {"error": "Coupon code already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the discount code without checking if the order exists
        coupon_code = CouponCode.objects.create(
            code=code,
            order_n=nth_order
        )

        return Response({
            "coupon_code": coupon_code.code,
            "message": f"Discount code generated for order #{nth_order}"
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(**report)
    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            total_items = CartItem.objects.aggregate(
                total_items=Sum('quantity')
            )['total_items'] or 0

            total_purchase = Order.objects.aggregate(
                total_purchase=Sum('total_amount')
            )['total_purchase'] or 0

            discount_codes_used = CouponCode.objects.filter(is_used=True).count()

            return Response({
                'total_items_purchased': total_items,
                'total_purchase_amount': total_purchase,
                'discount_codes_used': discount_codes_used
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
