from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from .models import Product, Category, ProductImage
from reviews.models import Review
import logging

logger = logging.getLogger(__name__)


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search)
            )

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['price', '-price', 'name', '-name', 'views_count', '-views_count']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        product.increment_views()

        context['images'] = product.images.all()

        reviews = Review.objects.filter(product=product, is_approved=True)
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context['review_form'] = None

        if self.request.user.is_authenticated:
            from reviews.forms import ReviewForm
            user_review = reviews.filter(user=self.request.user).first()
            if not user_review:
                context['review_form'] = ReviewForm()

        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:5]

        logger.info(f"Product viewed: {product.name} by {self.request.user or 'Anonymous'}")

        return context


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)

    context = {
        'category': category,
        'products': products,
        'categories': Category.objects.filter(is_active=True)
    }
    return render(request, 'products/category_products.html', context)
