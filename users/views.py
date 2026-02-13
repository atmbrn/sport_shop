from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    UserEditForm
)
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        logger.info(f"New user registered: {user.username}")
        messages.success(
            self.request,
            'Registration successful! You can now log in.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User logged in: {self.request.user.username}")
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return response


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('products:product_list')

    def get(self, request, *args, **kwargs):
        logger.info(f"User logged out: {request.user.username}")
        messages.success(request, "You have been logged out successfully.")
        return super().get(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['orders'] = self.request.user.orders.all()[:5]
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"Profile updated for user: {self.request.user.username}")
        messages.success(self.request, "Profile updated successfully!")
        return response


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'users/edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User information updated: {self.request.user.username}")
        messages.success(self.request, "Your information has been updated!")
        return response


@login_required(login_url='users:login')
def profile(request):
    profile_obj = request.user.profile
    context = {
        'user': request.user,
        'profile': profile_obj,
        'orders': request.user.orders.all()[:5]
    }
    return render(request, 'users/profile.html', context)
