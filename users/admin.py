from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        (None, {'fields': ('phone_number', 'bio')}),
        ('Personal Info', {'fields': ('gender', 'birth_date')}),
        ('Address', {'fields': ('address', 'city', 'postal_code')}),
        ('Media', {'fields': ('profile_image',)}),
        ('Preferences', {'fields': ('is_newsletter_subscriber',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'city',
        'gender',
        'created_at',
    )
    list_filter = (
        'gender',
        'is_newsletter_subscriber',
        'created_at',
    )
    search_fields = (
        'user__username',
        'user__email',
        'phone_number',
        'city',
    )
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Contact Info', {'fields': ('phone_number', 'address', 'city', 'postal_code')}),
        ('Personal Info', {'fields': ('gender', 'birth_date', 'bio')}),
        ('Media', {'fields': ('profile_image',)}),
        ('Preferences', {'fields': ('is_newsletter_subscriber',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
