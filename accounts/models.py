from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    # Defining my user roles
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('expert', 'Expert'),
    )

    # Table to store user roles
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_image = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(max_length=500, null=True, blank=True)

    # Expert-specific fields
    specialties = models.CharField(max_length=250, null=True, blank=True,
                                   help_text='Comma separated list of specialties')
    credentials = models.TextField(null=True, blank=True, help_text='Qualifications and credentials')
    available = models.BooleanField(default=True, help_text='Is the expert currently available?')

    # Ratings (calculated from reviews if added later)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.IntegerField(default=0)

    # Methods for the User models
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    def is_farmer(self):
        return self.user_type == 'farmer'
    
    def is_expert(self):
        return self.user_type == 'expert'

    def get_specialties_list(self):
        if not self.specialties:
            return []
        return [s.strip() for s in self.specialties.split(',') if s.strip()]

    @property
    def unread_notifications_count(self):
        try:
            return self.notifications.filter(unread=True).count()
        except Exception:
            return 0


class Notification(models.Model):
    """Simple in-app notification model."""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    verb = models.CharField(max_length=255)
    # CHANGE THIS LINE: Use string reference instead of direct import
    target_report = models.ForeignKey('farmcare.Report', null=True, blank=True, on_delete=models.SET_NULL)  # Changed to SET_NULL
    url = models.CharField(max_length=255, null=True, blank=True)
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient} - {self.verb[:40]}"