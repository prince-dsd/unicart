from .models import Cart, Product, CartItem, Order, CouponCode
import random
import string


class CartService:
    @staticmethod
    def add_items_to_cart(user, products):
        cart, _ = Cart.objects.get_or_create(user=user)

        for product_data in products:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity', 1)

            if not product_id or not isinstance(quantity, int) or quantity < 1:
                raise ValueError("Each product must have a valid product_id and a positive quantity.")

            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        # Recalculate total amount
        cart.total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
        cart.save()
        return cart


class OrderService:
    @staticmethod
    def checkout_cart(user, coupon_code):
        cart = Cart.objects.get(user=user)
        if not cart.items.exists():
            raise ValueError("Cart is empty.")

        discount_code = None
        discount_amount = 0

        if coupon_code:
            discount_code = CouponCode.objects.get(code=coupon_code, is_used=False)
            last_order = Order.objects.filter(user=user).order_by('-order_number').first()
            next_order_number = 1 if not last_order else last_order.order_number + 1

            if discount_code.order_n and next_order_number == discount_code.order_n:
                discount_amount = cart.total_amount * (discount_code.discount_percentage / 100)
                cart.total_amount -= discount_amount
            else:
                raise ValueError(f"Coupon code is not valid for order #{next_order_number}.")

        # Calculate total items purchased
        total_items_purchased = cart.items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

        # Create the order
        order = Order.objects.create(
            user=user,
            discount_code=discount_code,
            total_amount=cart.total_amount,
            total_discount_amount=discount_amount,
            total_items_purchased=total_items_purchased
        )

        # Mark the coupon code as used
        if discount_code:
            discount_code.is_used = True
            discount_code.save()

        # Delete the cart
        cart.delete()
        return order

    @staticmethod
    def generate_report():
        orders = Order.objects.all()
        order_details = [
            {
                "order_number": order.order_number,
                "user": order.user.username,
                "total_items_purchased": order.total_items_purchased,
                "total_purchase_amount": order.total_amount,
                "discount_code": order.discount_code.code if order.discount_code else None,
                "discount_amount": order.total_discount_amount
            }
            for order in orders
        ]

        summary = {
            "total_items_purchased": orders.aggregate(total_items=Sum('total_items_purchased'))['total_items'] or 0,
            "total_purchase_amount": orders.aggregate(total_purchase=Sum('total_amount'))['total_purchase'] or 0,
            "total_discount_amount": orders.aggregate(total_discount=Sum('total_discount_amount'))['total_discount'] or 0
        }

        return {"orders": order_details, "summary": summary}


class CouponService:
    @staticmethod
    def generate_discount_code(nth_order):
        if not isinstance(nth_order, int) or nth_order < 1:
            raise ValueError("nth_order must be a positive integer.")

        # Generate a random 6-digit alphanumeric code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Ensure the generated code is unique
        while CouponCode.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        return CouponCode.objects.create(code=code, order_n=nth_order)