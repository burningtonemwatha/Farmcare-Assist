from django import forms
from django.contrib.auth import get_user_model
from .models import Report

User = get_user_model()

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('title', 'description', 'issue_type', 'photo', 'assigned_to')
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

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),   # temporarily empty
        required=False,
        label='Assign Expert (optional)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FILTER EXPERTS DYNAMICALLY
        self.fields['assigned_to'].queryset = User.objects.filter(user_type='expert')