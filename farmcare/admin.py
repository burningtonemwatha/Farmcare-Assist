from django.contrib import admin
from .models import Report, Payment


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'issue_type', 'status', 'payment_status', 'amount', 'created_at']
    list_filter = ['status', 'payment_status', 'issue_type', 'created_at']
    search_fields = ['title', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Report Info', {
            'fields': ('user', 'title', 'issue_type', 'assigned_to')
        }),
        ('Details', {
            'fields': ('description', 'photo')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_status', 'amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make payment status readonly for non-superusers"""
        if not request.user.is_superuser:
            return self.readonly_fields + ('payment_status',)
        return self.readonly_fields


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'user', 'amount', 'phone_number', 'transaction_status', 'created_at']
    list_filter = ['transaction_status', 'payment_method', 'created_at']
    search_fields = ['report__title', 'user__username', 'mpesa_receipt_number', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Payment Info', {
            'fields': ('report', 'user', 'amount', 'phone_number', 'payment_method')
        }),
        ('Transaction Status', {
            'fields': ('transaction_status',)
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_checkout_request_id', 'mpesa_merchant_request_id', 
                      'mpesa_result_code', 'mpesa_result_description', 'mpesa_receipt_number'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make most fields readonly once payment is created"""
        if obj:  # Editing an existing object
            return self.readonly_fields + (
                'report', 'user', 'amount', 'phone_number', 'payment_method',
                'mpesa_checkout_request_id', 'mpesa_merchant_request_id',
                'mpesa_result_code', 'mpesa_result_description', 'mpesa_receipt_number'
            )
        return self.readonly_fields