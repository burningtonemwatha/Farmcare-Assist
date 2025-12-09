from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    """Form for creating and editing farm issue reports"""
    
    class Meta:
        model = Report
        fields = ('title', 'description', 'issue_type', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Report title (e.g., "Black Spot on Tomato Leaves")',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the issue in detail...',
                'rows': 5,
            }),
            'issue_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
