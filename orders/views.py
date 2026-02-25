from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


@login_required(login_url='users:login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    context = {
        'cart': cart,
        'items': cart.items.all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }
    return render(request, 'orders/cart.html', context)


@login_required(login_url='users:login')
def add_to_cart(request, product_id):
    variant_slug = request.POST.get('variant_slug') or None
    if variant_slug:
        product = get_object_or_404(Product, slug=variant_slug, is_active=True)
    else:
        product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items available.")
        return redirect('products:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()

    logger.info(f"Product added to cart: {product.name} (qty: {quantity}) by {request.user.username}")
    messages.success(request, f"{product.name} added to cart!")

    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    return redirect('orders:cart')


@login_required(login_url='users:login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()

    logger.info(f"Product removed from cart: {product_name} by {request.user.username}")
    messages.success(request, f"{product_name} removed from cart!")

    return redirect('orders:cart')


@login_required(login_url='users:login')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.success(request, f"{cart_item.product.name} removed from cart!")
    elif quantity > cart_item.product.stock:
        messages.error(request, f"Only {cart_item.product.stock} items available.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        logger.info(f"Cart item quantity updated: {cart_item.product.name} (qty: {quantity}) by {request.user.username}")
        messages.success(request, "Cart updated!")

    return redirect('orders:cart')


@login_required(login_url='users:login')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('orders:cart')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'card')

        order = Order.objects.create(
            user=request.user,
            status='pending',
            payment_method=payment_method,
            total_amount=cart.get_total_price(),
            final_amount=cart.get_total_price(),
            shipping_address=request.POST.get('shipping_address'),
            shipping_city=request.POST.get('shipping_city'),
            shipping_postal_code=request.POST.get('postal_code'),
            phone_number=request.POST.get('phone_number'),
            notes=request.POST.get('notes', '')
        )

        if payment_method == 'card' and request.POST.get('card_number'):
            raw = request.POST.get('card_number', '').replace(' ', '')
            last4 = raw[-4:] if len(raw) >= 4 else raw
            order.is_paid = True
            extra_note = f"\nPayment: Card ending ****{last4} (mock)."
            order.notes = (order.notes or '') + extra_note
            order.save()
            logger.info(f"Mock card payment applied for order {order.order_number} (****{last4})")

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.current_price,
            )

        cart.items.all().delete()

        logger.info(f"Order created: {order.order_number} by {request.user.username}")
        messages.success(request, "Order placed successfully!")

        return redirect('orders:order_detail', order_id=order.id)

    profile = request.user.profile
    context = {
        'cart': cart,
        'profile': profile,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'orders/checkout.html', context)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.get_object().items.all()
        return context


@login_required(login_url='users:login')
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "Order is already paid.")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'card')

        # Card processing (mock)
        if payment_method == 'card' and request.POST.get('card_number'):
            raw = request.POST.get('card_number', '').replace(' ', '')
            last4 = raw[-4:] if len(raw) >= 4 else raw
            order.is_paid = True
            extra_note = f"\nPayment: Card ending ****{last4} (mock)."
            order.notes = (order.notes or '') + extra_note
            order.payment_method = payment_method
            order.save()
            logger.info(f"Mock card payment applied for order {order.order_number} (****{last4})")
            messages.success(request, "Payment successful!")
            return redirect('orders:order_detail', order_id=order.id)

        # PayPal - redirect to a simple mock PayPal flow
        if payment_method == 'paypal':
            return redirect('orders:paypal_checkout', order_id=order.id)

        messages.error(request, "Please provide payment details.")
        return redirect('orders:pay_order', order_id=order.id)

    return render(request, 'orders/pay_order.html', {'order': order})


@login_required(login_url='users:login')
def paypal_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "Order is already paid.")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        # Simulate PayPal completing payment
        order.is_paid = True
        order.payment_method = 'paypal'
        extra_note = f"\nPayment: PayPal (mock) on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC."
        order.notes = (order.notes or '') + extra_note
        order.save()
        logger.info(f"Mock PayPal payment applied for order {order.order_number}")
        messages.success(request, "PayPal payment successful!")
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/paypal_checkout.html', {'order': order})
