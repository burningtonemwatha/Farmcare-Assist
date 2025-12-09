from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Report
from .forms import ReportForm

# Create your views here.

def is_expert(user):
    """Check if user is an expert"""
    return user.is_authenticated and user.user_type == 'expert'

@login_required
def dashboard_view(request):
    """User dashboard view"""
    user_reports = Report.objects.filter(user=request.user).count()
    context = {
        'user': request.user,
        'user_reports': user_reports,
    }
    return render(request, 'farmcare/dashboard.html', context)

@login_required
def report_create_view(request):
    """Create a new farm issue report"""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, 'Report created successfully!')
            return redirect('farmcare:reports')
    else:
        form = ReportForm()
    
    return render(request, 'farmcare/report_create.html', {'form': form})

@login_required
def reports_list_view(request):
    """List all user's reports"""
    reports = Report.objects.filter(user=request.user)
    context = {
        'reports': reports,
    }
    return render(request, 'farmcare/reports_list.html', context)

@login_required
def report_detail_view(request, pk):
    """View a single report"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    return render(request, 'farmcare/report_detail.html', {'report': report})

@login_required
def report_edit_view(request, pk):
    """Edit a report"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated successfully!')
            return redirect('farmcare:report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    
    return render(request, 'farmcare/report_edit.html', {'form': form, 'report': report})

@login_required
def farm_dashboard_view(request):
    """Farm dashboard view"""
    return render(request, 'farmcare/farm_dashboard.html')

# Expert views
@login_required
def expert_dashboard_view(request):
    """Expert dashboard - view all reports"""
    if not is_expert(request.user):
        return HttpResponseForbidden('You are not an expert.')
    
    # Get all reports, optionally filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_reports = Report.objects.filter(status=status_filter)
    else:
        all_reports = Report.objects.all()
    
    # Count reports by status
    pending = Report.objects.filter(status='pending').count()
    in_progress = Report.objects.filter(status='in_progress').count()
    resolved = Report.objects.filter(status='resolved').count()
    
    context = {
        'all_reports': all_reports,
        'pending_count': pending,
        'in_progress_count': in_progress,
        'resolved_count': resolved,
        'selected_status': status_filter,
    }
    return render(request, 'farmcare/expert_dashboard.html', context)

@login_required
def expert_report_detail_view(request, pk):
    """Expert view a report and update status"""
    if not is_expert(request.user):
        return HttpResponseForbidden('You are not an expert.')
    
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.assigned_to = request.user
            report.save()
            messages.success(request, f'Report status updated to {report.get_status_display()}!')
            return redirect('farmcare:expert_report_detail', pk=report.pk)
    
    return render(request, 'farmcare/expert_report_detail.html', {'report': report})
