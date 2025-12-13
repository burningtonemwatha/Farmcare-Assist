from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

class Report(models.Model):
    """Model for farm issue/pest reports"""
    
    ISSUE_TYPE_CHOICES = (
        ('pest', 'Pest'),
        ('disease', 'Disease'),
        ('weather', 'Weather Damage'),
        ('soil', 'Soil Issue'),
        ('water', 'Water/Irrigation'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('failed', 'Payment Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES, default='pest')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')
    
    # Payment fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)  # Default 500 KES
    
    # Cloudinary field for image upload
    photo = CloudinaryField('image', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Payment(models.Model):
    """Model for M-Pesa payment transactions"""
    
    PAYMENT_METHOD_CHOICES = (
        ('mpesa', 'M-Pesa'),
    )
    
    TRANSACTION_STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)  # M-Pesa phone number
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mpesa')
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='initiated')
    
    # M-Pesa specific fields
    mpesa_checkout_request_id = models.CharField(max_length=200, blank=True, null=True)
    mpesa_merchant_request_id = models.CharField(max_length=200, blank=True, null=True)
    mpesa_result_code = models.CharField(max_length=10, blank=True, null=True)
    mpesa_result_description = models.TextField(blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.transaction_status}"