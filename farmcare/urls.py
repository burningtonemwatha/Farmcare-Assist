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
]
