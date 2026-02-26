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

        reviews_qs = Review.objects.filter(product=product, is_approved=True)

        avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] or 0

        reviews_list = list(reviews_qs)

        if self.request.user.is_authenticated:
            from reviews.models import ReviewVote
            votes_qs = ReviewVote.objects.filter(review__in=reviews_qs, user=self.request.user).values_list('review_id', 'vote')
            vote_map = {rid: v for rid, v in votes_qs}
            for r in reviews_list:
                r.user_vote = vote_map.get(r.id, 0)
        else:
            for r in reviews_list:
                r.user_vote = 0

        context['reviews'] = reviews_list
        context['avg_rating'] = avg_rating
        context['review_form'] = None

        if self.request.user.is_authenticated:
            from reviews.forms import ReviewForm
            user_review = reviews_qs.filter(user=self.request.user).first()
            if not user_review:
                context['review_form'] = ReviewForm()

        context['related_products'] = Product.objects.filter(
            categories__in=product.categories.all(),
            is_active=True
        ).exclude(id=product.id)[:5]

        logger.info(f"Product viewed: {product.name} by {self.request.user or 'Anonymous'}")

        first_category = product.categories.first()
        if first_category:
            variants_qs = Product.objects.filter(
                name=product.name,
                categories=first_category,
                is_active=True
            ).order_by('size')
        else:
            variants_qs = Product.objects.filter(
                name=product.name,
                is_active=True
            ).order_by('size')
        context['variants'] = variants_qs

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


def home(request):
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)
