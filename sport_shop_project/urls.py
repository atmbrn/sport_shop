"""
URL configuration for sport_shop_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from products import views as products_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', products_views.home, name='home'),
    path('api-auth/', include('rest_framework.urls')),

    # App URLs
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),

    # API URLs
    path('api/v1/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
