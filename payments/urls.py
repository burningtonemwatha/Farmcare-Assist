# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:report_id>/', views.checkout_view, name='checkout'),
    path('status/<int:payment_id>/', views.payment_status_view, name='status'),
    path('check-status/<int:payment_id>/', views.check_payment_status_ajax, name='check_status'),
]