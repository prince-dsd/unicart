from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register('cart', CartViewSet, basename='cart')

# URL patterns including all cart endpoints
urlpatterns = [
    path('', include(router.urls)),
]

# The above configuration will automatically create the following URLs:
# POST /api/cart/add_item/ - Add items to cart
# POST /api/cart/{pk}/checkout/ - Checkout cart with optional discount code
# POST /api/cart/generate_discount_code/ - Admin API to generate discount codes
# GET /api/cart/report/ - Admin API to get sales report
