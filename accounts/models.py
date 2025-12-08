from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    # Defining my user roles
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('expert', 'Expert'),
    )

    # Table to store user roles
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)

    # Methods for the User models
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    def is_farmer(self):
        return self.user_type == 'farmer'
    
    def is_expert(self):
        return self.user_type == 'expert'