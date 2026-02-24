from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Review
from .forms import ReviewForm
import logging
from django.db import transaction
from .models import ReviewVote

logger = logging.getLogger(__name__)


@login_required(login_url='users:login')
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).first()

    if existing_review:
        messages.error(request, "You have already reviewed this product.")
        return redirect('products:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            from orders.models import OrderItem
            is_purchased = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__is_paid=True
            ).exists()
            review.is_verified_purchase = is_purchased

            review.save()
            logger.info(f"Review created for {product.name} by {request.user.username}")
            messages.success(request, "Your review has been submitted for approval!")
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'reviews/create_review.html', context)


@login_required(login_url='users:login')
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            logger.info(f"Review updated for {review.product.name} by {request.user.username}")
            messages.success(request, "Review updated successfully!")
            return redirect('products:product_detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'product': review.product,
        'is_edit': True,
    }
    return render(request, 'reviews/create_review.html', context)


@login_required(login_url='users:login')
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()

    logger.info(f"Review deleted for {review.product.name} by {request.user.username}")
    messages.success(request, "Review deleted successfully!")

    return redirect('products:product_detail', slug=product_slug)


@login_required(login_url='users:login')
def mark_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        with transaction.atomic():
            existing = ReviewVote.objects.filter(review=review, user=request.user).first()
            if existing:
                if existing.vote == ReviewVote.VOTE_HELPFUL:
                    existing.delete()
                    review.helpful_count = max(0, review.helpful_count - 1)
                    review.save()
                else:
                    existing.vote = ReviewVote.VOTE_HELPFUL
                    existing.save()
                    review.helpful_count += 1
                    review.unhelpful_count = max(0, review.unhelpful_count - 1)
                    review.save()
            else:
                ReviewVote.objects.create(review=review, user=request.user, vote=ReviewVote.VOTE_HELPFUL)
                review.helpful_count += 1
                review.save()
            logger.info(f"Review marked as helpful: {review.id} by {request.user.username}")

    return redirect('products:product_detail', slug=review.product.slug)


@login_required(login_url='users:login')
def mark_unhelpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        with transaction.atomic():
            existing = ReviewVote.objects.filter(review=review, user=request.user).first()
            if existing:
                if existing.vote == ReviewVote.VOTE_UNHELPFUL:
                    existing.delete()
                    review.unhelpful_count = max(0, review.unhelpful_count - 1)
                    review.save()
                else:
                    existing.vote = ReviewVote.VOTE_UNHELPFUL
                    existing.save()
                    review.unhelpful_count += 1
                    review.helpful_count = max(0, review.helpful_count - 1)
                    review.save()
            else:
                ReviewVote.objects.create(review=review, user=request.user, vote=ReviewVote.VOTE_UNHELPFUL)
                review.unhelpful_count += 1
                review.save()
            logger.info(f"Review marked as unhelpful: {review.id} by {request.user.username}")

    return redirect('products:product_detail', slug=review.product.slug)
