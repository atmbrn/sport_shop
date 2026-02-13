from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
import logging

logger = logging.getLogger(__name__)


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    helpful_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    unhelpful_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    @property
    def average_rating(self):
        from django.db.models import Avg
        avg = Review.objects.filter(product=self.product).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        return round(avg, 1) if avg else 0

    @property
    def helpful_percentage(self):
        total = self.helpful_count + self.unhelpful_count
        if total > 0:
            return int((self.helpful_count / total) * 100)
        return 0
