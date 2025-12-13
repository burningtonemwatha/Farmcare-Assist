from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Report
from .forms import ReportForm
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from datetime import timedelta, datetime
from accounts.models import Notification

User = get_user_model()

# Create your views here.

def is_expert(user):
    """Check if user is an expert"""
    return user.is_authenticated and user.user_type == 'expert'

@login_required
def dashboard_view(request):
    """User dashboard view"""
    user_reports = Report.objects.filter(user=request.user).count()
    paid_reports = Report.objects.filter(user=request.user, payment_status='paid').count()
    
    context = {
        'user': request.user,
        'user_reports': user_reports,
        'paid_reports': paid_reports,
    }
    return render(request, 'farmcare/dashboard.html', context)

@login_required
def report_create_view(request):
    """Create a new farm issue report"""
    # Allow preselecting an expert via ?expert=<id>
    preselected = request.GET.get('expert')

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            
            # Set payment status based on whether expert is assigned
            if report.assigned_to:
                report.payment_status = 'unpaid'  # Needs payment before expert can respond
            else:
                report.payment_status = 'unpaid'
            
            report.save()
            
            # Create notification if expert was assigned
            if report.assigned_to:
                Notification.objects.create(
                    recipient=report.assigned_to,
                    actor=request.user,
                    verb=f"New report '{report.title}' assigned to you.",
                    target_report=report,
                    url=f"/farmcare/expert/report/{report.pk}/"
                )
                messages.success(request, f'Report created and assigned to {report.assigned_to.username}! Payment required before expert can respond.')
            else:
                messages.success(request, 'Report created successfully! System will assign an expert. Payment required before expert can respond.')
            
            return redirect('farmcare:reports')
    else:
        if preselected:
            try:
                expert = User.objects.get(pk=int(preselected), user_type='expert')
                form = ReportForm(initial={'assigned_to': expert.pk})
            except Exception:
                form = ReportForm()
        else:
            form = ReportForm()

    # Provide link to experts directory
    experts_count = User.objects.filter(user_type='expert', available=True).count()

    return render(request, 'farmcare/report_create.html', {
        'form': form, 
        'experts_count': experts_count
    })

@login_required
def reports_list_view(request):
    """List all user's reports"""
    reports = Report.objects.filter(user=request.user)
    
    # Check payment status for each report
    for report in reports:
        if report.payment_status == 'unpaid' and hasattr(report, 'payments'):
            latest_payment = report.payments.first()
            if latest_payment and latest_payment.transaction_status == 'pending':
                report.payment_status = 'pending'
                report.save()
    
    context = {
        'reports': reports,
    }
    return render(request, 'farmcare/reports_list.html', context)

@login_required
def report_detail_view(request, pk):
    """View a single report"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    # Check if payment is pending
    if report.payment_status == 'unpaid' and hasattr(report, 'payments'):
        latest_payment = report.payments.first()
        if latest_payment and latest_payment.transaction_status == 'pending':
            report.payment_status = 'pending'
            report.save()
    
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
    reports = Report.objects.filter(user=request.user)
    paid_count = reports.filter(payment_status='paid').count()
    unpaid_count = reports.filter(payment_status='unpaid').count()
    
    context = {
        'total_reports': reports.count(),
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
    }
    return render(request, 'farmcare/farm_dashboard.html', context)

# Expert views
@login_required
def expert_dashboard_view(request):
    """Expert dashboard - view all reports"""
    if not is_expert(request.user):
        return HttpResponseForbidden('You are not an expert.')
    
    # Count reports by status
    pending = Report.objects.filter(status='pending').count()
    in_progress = Report.objects.filter(status='in_progress').count()
    resolved = Report.objects.filter(status='resolved').count()

    # Determine recent window for spikes (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Farmers with their total report counts and recent report counts
    farmers = (
        User.objects.filter(user_type='farmer')
        .annotate(
            report_count=Count('reports'),
            recent_count=Count('reports', filter=Q(reports__created_at__gte=seven_days_ago))
        )
        .order_by('-report_count')[:100]
    )

    # Top issue types across all reports
    top_issues_qs = Report.objects.values('issue_type').annotate(count=Count('id')).order_by('-count')[:10]
    # Map code to readable label
    issue_map = dict(Report.ISSUE_TYPE_CHOICES)
    top_issues = [{'issue_type': item['issue_type'], 'label': issue_map.get(item['issue_type'], item['issue_type']), 'count': item['count']} for item in top_issues_qs]

    # Recent paid reports for quick review
    recent_reports = Report.objects.filter(payment_status='paid').order_by('-created_at')[:10]

    context = {
        'pending_count': pending,
        'in_progress_count': in_progress,
        'resolved_count': resolved,
        'farmers': farmers,
        'top_issues': top_issues,
        'recent_reports': recent_reports,
    }
    return render(request, 'farmcare/expert_dashboard.html', context)


@login_required
def farmer_detail_view(request, pk):
    """Detail page for a farmer — shows their profile and recent reports.

    Querystring `paid=1` will show only paid reports; otherwise shows all.
    """
    farmer = get_object_or_404(User, pk=pk, user_type='farmer')

    paid_only = request.GET.get('paid') in ('1', 'true', 'True')

    if paid_only:
        reports = farmer.reports.filter(payment_status='paid').order_by('-created_at')
    else:
        reports = farmer.reports.all().order_by('-created_at')

    context = {
        'farmer': farmer,
        'reports': reports,
        'paid_only': paid_only,
    }

    return render(request, 'farmcare/farmer_detail.html', context)


@login_required
@require_POST
def assign_report_to_me(request, pk):
    """Assign the given report to the current logged-in expert.

    Only experts can assign themselves, and only for paid reports.
    """
    if not is_expert(request.user):
        return HttpResponseForbidden('Only experts can assign reports to themselves.')

    report = get_object_or_404(Report, pk=pk)

    # Only allow assignment if the report is paid
    if report.payment_status != 'paid':
        messages.error(request, 'You can only assign yourself to reports that have been paid for.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # If already assigned to someone else, prevent overwrite
    if report.assigned_to and report.assigned_to != request.user:
        messages.error(request, f'Report already assigned to {report.assigned_to.get_full_name() or report.assigned_to.username}.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    report.assigned_to = request.user
    report.status = 'in_progress'
    report.save()

    # Create notifications for the farmer and the expert
    try:
        # Notify farmer
        Notification.objects.create(
            recipient=report.user,
            actor=request.user,
            verb=f"{request.user.get_full_name() or request.user.username} has been assigned to your report '{report.title}'.",
            target_report=report,
            url=f"/farmcare/report/{report.pk}/"
        )
        # Notify expert (self)
        Notification.objects.create(
            recipient=request.user,
            actor=request.user,
            verb=f"You are assigned to report '{report.title}'.",
            target_report=report,
            url=f"/farmcare/expert/report/{report.pk}/"
        )
    except Exception as e:
        # If notification creation fails, log the error
        print(f"Error creating notification: {e}")  # In production, use logging instead

    messages.success(request, 'You are now assigned to this report. Open it to start working.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def unassign_report(request, pk):
    """Allow an expert to unassign themselves from a report they own (or superuser)."""
    report = get_object_or_404(Report, pk=pk)

    if not request.user.is_superuser and report.assigned_to != request.user:
        return HttpResponseForbidden('You are not allowed to unassign this report.')

    previous_assignee = report.assigned_to
    report.assigned_to = None
    report.status = 'pending'
    report.save()

    # Create notification for farmer and previous assignee
    try:
        if report.user:
            Notification.objects.create(
                recipient=report.user,
                actor=request.user,
                verb=f"{request.user.get_full_name() or request.user.username} has unassigned themselves from report '{report.title}'.",
                target_report=report,
                url=f"/farmcare/report/{report.pk}/"
            )
        if previous_assignee and previous_assignee != request.user:
            Notification.objects.create(
                recipient=previous_assignee,
                actor=request.user,
                verb=f"You have been unassigned from report '{report.title}'.",
                target_report=report,
                url=f"/farmcare/report/{report.pk}/"
            )
    except Exception as e:
        print(f"Error creating notification: {e}")  # In production, use logging instead

    messages.success(request, 'Report unassigned.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def expert_report_detail_view(request, pk):
    """Expert view a report and update status"""
    if not is_expert(request.user):
        return HttpResponseForbidden('You are not an expert.')
    
    report = get_object_or_404(Report, pk=pk)
    
    # Check if report is paid
    if report.payment_status != 'paid':
        messages.error(request, 'This report has not been paid for yet. Expert response is not allowed.')
        return redirect('farmcare:expert_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            if not report.assigned_to:
                report.assigned_to = request.user
            report.save()
            
            # Notify farmer about status update
            try:
                Notification.objects.create(
                    recipient=report.user,
                    actor=request.user,
                    verb=f"Your report '{report.title}' status has been updated to '{report.get_status_display()}'.",
                    target_report=report,
                    url=f"/farmcare/report/{report.pk}/"
                )
            except Exception as e:
                print(f"Error creating notification: {e}")
            
            messages.success(request, f'Report status updated to {report.get_status_display()}!')
            return redirect('farmcare:expert_report_detail', pk=report.pk)
    
    return render(request, 'farmcare/expert_report_detail.html', {
        'report': report,
        'is_expert': True,
    })


@login_required
def experts_list_view(request):
    """List available experts so farmers can choose one"""
    experts = User.objects.filter(
        user_type='expert', 
        available=True
    ).order_by('username')
    
    return render(request, 'farmcare/experts_list.html', {'experts': experts})


@login_required
def expert_profile_view(request, pk):
    """Public expert profile so farmers can inspect credentials before selecting"""
    expert = get_object_or_404(User, pk=pk, user_type='expert')

    context = {
        'expert': expert,
    }
    return render(request, 'farmcare/expert_detail.html', context)


# Payment redirect views - Redirect to payments app
@login_required
def payment_checkout_view(request, pk):
    """Redirect to payments app checkout"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    # Check if already paid
    if report.payment_status == 'paid':
        messages.info(request, 'This report has already been paid for.')
        return redirect('farmcare:report_detail', pk=report.pk)
    
    # Redirect to payments app
    return redirect('payments:checkout', report_id=report.pk)


@login_required
def payment_status_view(request, pk):
    """Redirect to payments app status page"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    # Get latest payment
    from .models import Payment
    payment = report.payments.first()
    
    if not payment:
        return redirect('farmcare:payment_checkout', pk=report.pk)
    
    # Redirect to payments app
    return redirect('payments:status', payment_id=payment.pk)


# M-Pesa callback - Keep this in farmcare since it updates both models
@csrf_exempt
@require_POST
def mpesa_callback_view(request):
    """M-Pesa callback endpoint - MUST be publicly accessible"""
    try:
        data = json.loads(request.body)
        
        # Import here to avoid circular import
        from .mpesa_service import get_mpesa_service
        mpesa_service = get_mpesa_service(use_sandbox=True)
        callback_info = mpesa_service.process_callback(data)
        
        if 'error' in callback_info:
            return JsonResponse({'error': callback_info['error']}, status=400)
        
        # Find payment by checkout request ID
        checkout_request_id = callback_info.get('checkout_request_id')
        if not checkout_request_id:
            return JsonResponse({'error': 'No CheckoutRequestID'}, status=400)
        
        from .models import Payment
        payment = Payment.objects.filter(mpesa_checkout_request_id=checkout_request_id).first()
        
        if not payment:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        result_code = callback_info.get('result_code')
        result_description = callback_info.get('result_description', '')
        metadata = callback_info.get('metadata', {})
        
        # Update payment
        payment.mpesa_result_code = result_code
        payment.mpesa_result_description = result_description
        payment.mpesa_merchant_request_id = callback_info.get('merchant_request_id')
        
        if result_code == '0':
            # Successful payment
            payment.transaction_status = 'success'
            payment.mpesa_receipt_number = metadata.get('ReceiptNumber')
            
            # Update report payment status
            report = payment.report
            report.payment_status = 'paid'
            report.save()
            
            # Notify farmer about successful payment
            try:
                Notification.objects.create(
                    recipient=report.user,
                    actor=report.user,  # The farmer themselves
                    verb=f"Payment for report '{report.title}' was successful. Expert can now respond.",
                    target_report=report,
                    url=f"/farmcare/report/{report.pk}/"
                )
            except Exception as e:
                print(f"Error creating notification: {e}")
        else:
            # Failed payment
            payment.transaction_status = 'failed'
            
            # Notify farmer about failed payment
            try:
                report = payment.report
                Notification.objects.create(
                    recipient=report.user,
                    actor=report.user,  # The farmer themselves
                    verb=f"Payment for report '{report.title}' failed. Please try again.",
                    target_report=report,
                    url=f"/payments/checkout/{report.pk}/"
                )
            except Exception as e:
                print(f"Error creating notification: {e}")
        
        payment.save()
        
        return JsonResponse({'success': True, 'message': 'Callback processed'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)