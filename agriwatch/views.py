from django.shortcuts import render


def home_view(request):
    """Simple homepage view."""
    return render(request, 'home.html')
