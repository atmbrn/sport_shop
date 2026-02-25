from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:product_id>/', views.create_review, name='create'),
    path('edit/<int:review_id>/', views.edit_review, name='edit'),
    path('delete/<int:review_id>/', views.delete_review, name='delete'),
    path('helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
    path('unhelpful/<int:review_id>/', views.mark_unhelpful, name='mark_unhelpful'),
]
