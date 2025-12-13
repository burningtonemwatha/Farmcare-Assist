# payments/admin.py
from django.contrib import admin
from farmcare.models import Payment

#@admin.register(Payment)
#class PaymentAdmin(admin.ModelAdmin):
#    list_display = ['id', 'report', 'user', 'amount', 'transaction_status', 'created_at']
#    list_filter = ['transaction_status', 'payment_method', 'created_at']
 #   search_fields = ['report__title', 'user__username', 'mpesa_receipt_number']
  #  readonly_fields = ['created_at', 'updated_at']
   # date_hierarchy = 'created_at'