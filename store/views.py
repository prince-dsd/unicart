from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal
from .models import Cart, Product, CouponCode, CartItem, Order
from .serializers import CartSerializer, OrderSerializer, CouponCodeSerializer  # Ensure the serializer is imported
from .swagger import cart_add_items, cart_checkout, generate_discount_code, report

class CartViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(**cart_add_items)
    @action(detail=False, methods=['post'], url_path='add-items')
    def add_item(self, request):
        user = request.user
        products = request.data.get('products', [])

        if not isinstance(products, list) or not products:
            return Response(
                {"error": "A list of products is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=user)

        for product_data in products:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity', 1)

            if not product_id or not isinstance(quantity, int) or quantity < 1:
                return Response(
                    {"error": "Each product must have a valid product_id and a positive quantity."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                product = Product.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            except Product.DoesNotExist:
                return Response(
                    {"error": f"Product with ID {product_id} not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Recalculate total amount
        cart.total_amount = sum(
            item.product.price * item.quantity
            for item in cart.items.all()
        )
        cart.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**cart_checkout)
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        user = request.user
        try:
            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(user=user)
            if created:
                cart.save()  # Ensure the cart is saved to the database

            if not cart.items.exists():
                return Response(
                    {"error": "Cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            coupon_code = request.data.get('coupon_code', '').strip()  # Accept empty string
            discount_code = None
            discount_amount = 0

            if coupon_code:  # Check if a coupon code is provided
                try:
                    # Fetch the coupon code
                    discount_code = CouponCode.objects.get(code=coupon_code, is_used=False)

                    # Check if the current order matches the `order_n` of the coupon
                    last_order = Order.objects.filter(user=user).order_by('-order_number').first()
                    next_order_number = 1 if not last_order else last_order.order_number + 1

                    if discount_code.order_n and next_order_number == discount_code.order_n:
                        # Apply the discount percentage
                        discount_amount = cart.total_amount * (discount_code.discount_percentage / 100)
                        cart.total_amount -= discount_amount
                    else:
                        return Response(
                            {
                                "error": f"Coupon code is not valid for order #{next_order_number}.",
                                "message": "Please change the coupon code or remove it."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except CouponCode.DoesNotExist:
                    return Response(
                        {
                            "error": "Invalid or used coupon code.",
                            "message": "Please change the coupon code or remove it."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Save the cart to ensure it has a primary key
            cart.save()

            # Create the order
            order = Order.objects.create(
                user=user,
                cart=cart,
                discount_code=discount_code,
                total_amount=cart.total_amount
            )

            # Mark the coupon code as used if it was applied
            if discount_code:
                discount_code.is_used = True
                discount_code.save()

            # Serialize the order response
            response_data = {
                'order': OrderSerializer(order).data,
                'message': f'Order #{order.order_number} created successfully'
            }

            # Delete the cart and associated cart items after serialization
            cart.delete()  # This will also delete all related CartItem objects due to the ForeignKey relationship

            return Response(response_data, status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(
        operation_summary="Get Unused Coupon Codes",
        operation_description="Retrieve all unused coupon codes along with their discount percentages.",
        responses={200: "List of unused coupon codes"}
    )
    @action(detail=False, methods=['get'], url_path='unused-coupons')
    def unused_coupons(self, request):
        """
        API to fetch all unused coupon codes and their discount percentages.
        """
        unused_coupons = CouponCode.objects.filter(is_used=False)  # Fetch unused coupon codes
        serializer = CouponCodeSerializer(unused_coupons, many=True)  # Serialize the data
        return Response(serializer.data, status=status.HTTP_200_OK)
