from django.contrib import admin
from .models import Category, Product, ProductImage
import logging

logger = logging.getLogger(__name__)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary')


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Category Info', {'fields': ('name', 'slug')}),
        ('Description', {'fields': ('description',)}),
        ('Media', {'fields': ('image',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_category',
        'price',
        'discount_price',
        'stock',
        'is_featured',
        'is_active',
        'views_count',
    )
    list_filter = (
        'categories',
        'is_featured',
        'is_active',
        'created_at',
        'size',
        'color',
    )
    search_fields = (
        'name',
        'description',
        'brand',
        'slug',
    )
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Product Info', {'fields': ('name', 'slug', 'category')}),
        ('Description', {'fields': ('description',)}),
        ('Pricing', {'fields': ('price', 'discount_price')}),
        ('Stock & Availability', {'fields': ('stock', 'is_active')}),
        ('Specifications', {'fields': ('size', 'color', 'brand', 'material')}),
        ('Media', {'fields': ('image',)}),
        ('Featured', {'fields': ('is_featured',)}),
        ('Analytics', {'fields': ('views_count',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'views_count')

    def get_categories(self, obj):
        return ', '.join([cat.name for cat in obj.categories.all()]) if obj.categories.exists() else ''
    get_categories.short_description = 'Categories'
    # keep compatibility name
    def get_category(self, obj):
        return ', '.join([cat.name for cat in obj.categories.all()]) if obj.categories.exists() else ''
    get_category.short_description = 'Categories'


class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'is_primary',
        'created_at',
    )
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    fieldsets = (
        ('Image Info', {'fields': ('product', 'image', 'alt_text')}),
        ('Status', {'fields': ('is_primary',)}),
        ('Created', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
