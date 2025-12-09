from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard_view(request):
    """User dashboard view"""
    return render(request, 'farmcare/dashboard.html', {'user': request.user})

@login_required
def report_create_view(request):
    """Create a new report"""
    return render(request, 'farmcare/report_create.html')

@login_required
def reports_list_view(request):
    """List all reports"""
    return render(request, 'farmcare/reports_list.html')

@login_required
def farm_dashboard_view(request):
    """Farm dashboard view"""
    return render(request, 'farmcare/farm_dashboard.html')
