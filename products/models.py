from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    categories = models.ManyToManyField(
        Category,
        related_name='products'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    size = models.CharField(
        max_length=5,
        choices=SIZE_CHOICES,
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        unique_together = ('name', 'size', 'color')

    def __str__(self):
        return f"{self.name} ({self.size or 'One size'})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        if self.discount_price:
            percentage = ((self.price - self.discount_price) / self.price) * 100
            return int(percentage)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"
