from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', views.update_cart_item, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:order_id>/pay/', views.pay_order, name='pay_order'),
    path('order/<int:order_id>/paypal/', views.paypal_checkout, name='paypal_checkout'),
]
