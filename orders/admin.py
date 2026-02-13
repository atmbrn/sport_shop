from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Cart, CartItem
import logging

logger = logging.getLogger(__name__)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'subtotal')
    readonly_fields = ('subtotal',)
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status_badge',
        'final_amount',
        'payment_status',
        'created_at',
    )
    list_filter = (
        'status',
        'is_paid',
        'payment_method',
        'created_at',
    )
    search_fields = (
        'order_number',
        'user__username',
        'user__email',
        'shipping_city',
    )
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'status')}),
        ('Payment', {'fields': ('is_paid', 'payment_method', 'final_amount')}),
        ('Amounts', {'fields': ('total_amount', 'discount_amount', 'shipping_cost')}),
        ('Shipping', {'fields': (
            'shipping_address',
            'shipping_city',
            'shipping_postal_code',
            'phone_number',
        )}),
        ('Additional', {'fields': ('notes',)}),
        ('Timeline', {'fields': (
            'created_at',
            'updated_at',
            'shipped_at',
            'delivered_at',
        ), 'classes': ('collapse',)}),
    )
    readonly_fields = (
        'order_number',
        'created_at',
        'updated_at',
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'processing': '#4169E1',
            'shipped': '#1E90FF',
            'delivered': '#228B22',
            'cancelled': '#DC143C',
        }
        color = colors.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_status(self, obj):
        if obj.is_paid:
            return format_html(
                '<span style="color: green;">✓ Paid</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Unpaid</span>'
        )
    payment_status.short_description = 'Payment Status'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity', 'added_at')
    readonly_fields = ('added_at',)


class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_items_count',
        'get_total_price',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]
    fieldsets = (
        ('Cart Info', {'fields': ('user',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_items_count(self, obj):
        count = obj.get_total_items()
        return f"{count} item(s)"
    get_items_count.short_description = 'Items'

    def get_total_price(self, obj):
        total = obj.get_total_price()
        return f"${total:.2f}"
    get_total_price.short_description = 'Total Price'


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'quantity',
        'price',
        'subtotal',
    )
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product__name')
    fieldsets = (
        ('Item Info', {'fields': ('order', 'product')}),
        ('Quantity & Price', {'fields': ('quantity', 'price', 'subtotal')}),
    )
    readonly_fields = ('subtotal',)


class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product',
        'quantity',
        'added_at',
    )
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'product__name')
    fieldsets = (
        ('Item Info', {'fields': ('cart', 'product')}),
        ('Quantity', {'fields': ('quantity',)}),
        ('Timestamps', {'fields': ('added_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('added_at', 'updated_at')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
