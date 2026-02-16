from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper
import logging

logger = logging.getLogger(__name__)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(
        max_length=20,
        unique=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='card'
    )
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    notes = models.TextField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"

    def get_items_count(self):
        return self.items.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    @property
    def status_display(self):
        return self.get_status_display()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        unit_price_expr = Coalesce(F('product__discount_price'), F('product__price'))
        total_expr = ExpressionWrapper(F('quantity') * unit_price_expr, output_field=DecimalField())
        return self.items.aggregate(
            total=Sum(total_expr)
        )['total'] or 0

    def get_total_items(self):
        return self.items.aggregate(
            total=Sum('quantity')
        )['total'] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} in {self.cart.user.username}'s cart"

    @property
    def subtotal(self):
        price = self.product.discount_price if self.product.discount_price is not None else self.product.price
        return price * self.quantity
