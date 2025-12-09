from django.urls import path
from . import views

app_name = 'farmcare'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('report/create/', views.report_create_view, name='report_create'),
    path('reports/', views.reports_list_view, name='reports'),
    path('farm/', views.farm_dashboard_view, name='farm_dashboard'),
]
