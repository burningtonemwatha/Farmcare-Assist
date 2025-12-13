from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget = forms.EmailInput(attrs={'class':'form-control',
                                                                             'placeholder':'Email'}))
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
    # Expert profile fields (optional during registration)
    profile_image = forms.FileField(required=False, widget=forms.FileInput(attrs={'class':'form-control'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Short bio'}))
    specialties = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Comma separated specialties'}))
    credentials = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Qualifications and credentials'}))
    available = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'password1', 'password2', 'profile_image', 'bio', 'specialties', 'credentials', 'available') # Include optional expert fields
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'})
            
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        # Save expert-only fields if provided
        user.bio = self.cleaned_data.get('bio')
        user.specialties = self.cleaned_data.get('specialties')
        user.credentials = self.cleaned_data.get('credentials')
        user.available = bool(self.cleaned_data.get('available'))
        profile_image = self.cleaned_data.get('profile_image')
        if profile_image:
            user.profile_image = profile_image
        if commit:
            user.save()
        return user

# User Login Form
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

# Profile form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'profile_image', 'specialties', 'credentials', 'available')
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}),
            'bio': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Bio'}),
            'profile_image': forms.FileInput(attrs={'class':'form-control'}),
            'specialties': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Comma separated specialties'}),
            'credentials': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Qualifications and credentials'}),
            'available': forms.CheckboxInput(),
        }