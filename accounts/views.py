from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm

# Create your views here.
# This view handles user account details

# User Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('farmcare:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Welcome {user.username}! Registration successful. Please log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('farmcare:dashboard')
    
    if request.method == 'POST':
        # AuthenticationForm (and subclasses) expect the request as the first arg
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            # AuthenticationForm provides the authenticated user via get_user()
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back {user.username}!')
            return redirect('farmcare:dashboard')
        else:
            # Let the form add its own error messages (will appear in messages)
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm(request)
    
    return render(request, 'accounts/login.html', {'form': form})

# User Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')

# User Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')