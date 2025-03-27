from django.contrib import admin
from .models import Product, Cart, Order, CouponCode, CartItem

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(CouponCode)
admin.site.register(CartItem)
