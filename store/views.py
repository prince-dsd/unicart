from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from drf_yasg.utils import swagger_auto_schema
from .models import Cart, Product, CouponCode, CartItem, Order
from .serializers import CartSerializer, OrderSerializer, CouponCodeSerializer
from .swagger import cart_add_items, cart_checkout, generate_discount_code, report
from .services import CartService, OrderService, CouponService


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for managing cart operations such as adding items, checkout, and generating reports.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(**cart_add_items)
    @action(detail=False, methods=['post'], url_path='add-items')
    def add_item(self, request):
        """
        Add multiple items to the user's cart.
        """
        user = request.user
        products = request.data.get('products', [])

        if not isinstance(products, list) or not products:
            return Response(
                {"error": "A list of products is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = CartService.add_items_to_cart(user, products)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except Product.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(**cart_checkout)
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Checkout the user's cart and create an order.
        """
        user = request.user
        coupon_code = request.data.get('coupon_code', '').strip()

        try:
            order = OrderService.checkout_cart(user, coupon_code)
            return Response(
                {
                    'order': OrderSerializer(order).data,
                    'message': f'Order #{order.order_number} created successfully'
                },
                status=status.HTTP_201_CREATED
            )
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except CouponCode.DoesNotExist:
            return Response(
                {"error": "Invalid or used coupon code.", "message": "Please change the coupon code or remove it."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(**generate_discount_code)
    @action(detail=False, methods=['post'], url_path='generate-discount-code')
    def generate_discount_code(self, request):
        """
        Generate a discount code for the nth order (Admin only).
        """
        if not request.user.is_staff:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        nth_order = request.data.get('nth_order')

        try:
            coupon_code = CouponService.generate_discount_code(nth_order)
            return Response(
                {
                    "coupon_code": coupon_code.code,
                    "message": f"Discount code generated for order #{nth_order}"
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(**report)
    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        """
        Generate a sales report (Admin only).
        """
        if not request.user.is_staff:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        try:
            report_data = OrderService.generate_report()
            return Response(report_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Get Unused Coupon Codes",
        operation_description="Retrieve all unused coupon codes along with their discount percentages.",
        responses={200: "List of unused coupon codes"}
    )
    @action(detail=False, methods=['get'], url_path='unused-coupons')
    def unused_coupons(self, request):
        """
        Retrieve all unused coupon codes and their discount percentages.
        """
        unused_coupons = CouponCode.objects.filter(is_used=False)
        serializer = CouponCodeSerializer(unused_coupons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
