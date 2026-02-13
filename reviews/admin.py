from django.contrib import admin
from django.utils.html import format_html
from .models import Review
import logging

logger = logging.getLogger(__name__)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating_display',
        'is_approved',
        'is_verified_purchase',
        'created_at',
    )
    list_filter = (
        'rating',
        'is_approved',
        'is_verified_purchase',
        'created_at',
    )
    search_fields = (
        'product__name',
        'user__username',
        'title',
        'content',
    )
    fieldsets = (
        ('Product & User', {'fields': ('product', 'user')}),
        ('Review Content', {'fields': ('title', 'content')}),
        ('Rating', {'fields': ('rating',)}),
        ('Feedback', {'fields': ('helpful_count', 'unhelpful_count')}),
        ('Status', {'fields': ('is_approved', 'is_verified_purchase')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_reviews', 'disapprove_reviews']

    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="font-size: 14px; color: #FFC107;">{}</span>',
            stars
        )
    rating_display.short_description = 'Rating'

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review(s) approved.')
    approve_reviews.short_description = 'Approve selected reviews'

    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review(s) disapproved.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'


admin.site.register(Review, ReviewAdmin)
