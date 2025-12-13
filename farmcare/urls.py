# farmcare/urls.py
from django.urls import path
from . import views

app_name = 'farmcare'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('report/create/', views.report_create_view, name='report_create'),
    path('reports/', views.reports_list_view, name='reports'),
    path('report/<int:pk>/', views.report_detail_view, name='report_detail'),
    path('report/<int:pk>/edit/', views.report_edit_view, name='report_edit'),
    path('farm/', views.farm_dashboard_view, name='farm_dashboard'),
    
    # Expert routes
    path('expert/dashboard/', views.expert_dashboard_view, name='expert_dashboard'),
    path('expert/report/<int:pk>/', views.expert_report_detail_view, name='expert_report_detail'),
    
    # Payment redirect routes - These redirect to payments app
    path('report/<int:pk>/payment/checkout/', views.payment_checkout_view, name='payment_checkout'),
    path('report/<int:pk>/payment/status/', views.payment_status_view, name='payment_status'),
    
    # M-Pesa callback - Keep this in farmcare
    path('payment/callback/', views.mpesa_callback_view, name='mpesa_callback'),
    
    # Other routes
    path('experts/', views.experts_list_view, name='experts'),
    path('experts/<int:pk>/', views.expert_profile_view, name='expert_profile'),
    path('farmer/<int:pk>/', views.farmer_detail_view, name='farmer_detail'),
    path('report/<int:pk>/assign/', views.assign_report_to_me, name='assign_report_to_me'),
    path('report/<int:pk>/unassign/', views.unassign_report, name='unassign_report'),
]