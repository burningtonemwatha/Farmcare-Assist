from django.urls import path
from . import views

## Registering the URL patterns for the accounts app
urlpatterns = [
    path('', views.home, name='home'),
]