from django.contrib import admin
from django.utils.html import format_html
from .models import Report, Payment


class PaidReportFilter(admin.SimpleListFilter):
    """Filter to show only paid reports"""
    title = 'Payment Status'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('paid', 'Paid'),
            ('pending', 'Pending Payment'),
            ('unpaid', 'Unpaid'),
            ('failed', 'Failed'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_status=self.value())
        return queryset


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin for reviewing paid reports - expert-focused order management"""
    
    list_display = ('order_id', 'farmer_name', 'issue_badge', 'status_badge', 'payment_icon', 'amount_display', 'created_at')
    list_filter = (PaidReportFilter, 'status', 'issue_type', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'farmer_details', 'payment_details')
    
    fieldsets = (
        ('Report Info', {
            'fields': ('title', 'issue_type', 'description', 'photo')
        }),
        ('Farmer Details', {
            'fields': ('farmer_details',),
            'classes': ('collapse',)
        }),
        ('Review Status', {
            'fields': ('status', 'assigned_to')
        }),
        ('Order Payment', {
            'fields': ('payment_details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_in_progress', 'mark_resolved', 'assign_to_me']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Only show PAID reports - farmers must pay first"""
        qs = super().get_queryset(request)
        return qs.filter(payment_status='paid').order_by('-created_at')
    
    def order_id(self, obj):
        return f"#ORD-{obj.pk}"
    order_id.short_description = 'Order ID'
    
    def farmer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    farmer_name.short_description = 'From Farmer'
    
    def issue_badge(self, obj):
        colors = {
            'pest': '#dc3545', 'disease': '#fd7e14', 'weather': '#0dcaf0',
            'soil': '#6f42c1', 'water': '#0d6efd', 'other': '#6c757d',
        }
        color = colors.get(obj.issue_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_issue_type_display()
        )
    issue_badge.short_description = 'Issue'
    
    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'in_progress': '#0dcaf0', 'resolved': '#198754'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_icon(self, obj):
        return format_html('<span style="color: green; font-size: 1.2em;">✓</span>') if obj.payment_status == 'paid' else format_html('<span style="color: red;">✗</span>')
    payment_icon.short_description = 'Paid'
    
    def amount_display(self, obj):
        return f"KES {obj.amount}"
    amount_display.short_description = 'Amount'
    
    def farmer_details(self, obj):
        return format_html(
            '<strong>{}</strong><br/>{}<br/><em>{}</em>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.user.get_user_type_display()
        )
    farmer_details.short_description = 'Farmer Information'
    
    def payment_details(self, obj):
        return format_html(
            '<strong>Status:</strong> {}<br/><strong>Amount:</strong> KES {}<br/><strong>Paid:</strong> Yes',
            obj.get_payment_status_display(), obj.amount
        )
    payment_details.short_description = 'Payment Details'
    
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status='in_progress', assigned_to=request.user)
        self.message_user(request, f'{count} order(s) marked as in progress.')
    mark_in_progress.short_description = '▶ Mark In Progress'
    
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved')
        self.message_user(request, f'{count} order(s) marked as resolved.')
    mark_resolved.short_description = '✓ Mark Resolved'
    
    def assign_to_me(self, request, queryset):
        count = queryset.update(assigned_to=request.user, status='in_progress')
        self.message_user(request, f'{count} order(s) assigned to you.')
    assign_to_me.short_description = '→ Assign to Me'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Order Payments - track all customer transactions"""
    
    list_display = ('order_pay_id', 'farmer_name', 'amount_display', 'status_badge', 'receipt_num', 'created_at')
    list_filter = ('transaction_status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'mpesa_receipt_number')
    readonly_fields = ('created_at', 'updated_at', 'mpesa_checkout_request_id', 'mpesa_merchant_request_id')
    
    fieldsets = (
        ('Order', {
            'fields': ('report', 'amount', 'phone_number')
        }),
        ('Payment Status', {
            'fields': ('payment_method', 'transaction_status')
        }),
        ('M-Pesa Receipt', {
            'fields': ('mpesa_receipt_number', 'mpesa_result_code', 'mpesa_result_description'),
        }),
        ('API Details', {
            'fields': ('mpesa_checkout_request_id', 'mpesa_merchant_request_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def order_pay_id(self, obj):
        return f"#PAY-{obj.pk}"
    order_pay_id.short_description = 'Payment ID'
    
    def farmer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    farmer_name.short_description = 'Farmer'
    
    def amount_display(self, obj):
        return f"KES {obj.amount}"
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'success': '#198754', 'pending': '#ffc107', 'failed': '#dc3545',
            'initiated': '#0dcaf0', 'cancelled': '#6c757d'
        }
        color = colors.get(obj.transaction_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_transaction_status_display()
        )
    status_badge.short_description = 'Status'
    
    def receipt_num(self, obj):
        return obj.mpesa_receipt_number or '—'
    receipt_num.short_description = 'Receipt'
