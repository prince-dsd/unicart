from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f'Cart for {self.user.username}'

class CouponCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=False)
    order_n = models.PositiveIntegerField(null=True, blank=True)  # Allow null and blank values
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # Default 10% discount
    
    def __str__(self):
        return self.code

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    discount_code = models.ForeignKey(CouponCode, null=True, blank=True, on_delete=models.SET_NULL)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.PositiveIntegerField(unique=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-order_number').first()
            self.order_number = 1 if not last_order else last_order.order_number + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order #{self.order_number} for {self.user.username}'
