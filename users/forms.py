from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import CustomUser


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email Address'
    }))

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'profile_picture', 'bio', 'date_of_birth', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Your Address',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:

            profile.save()
            
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling"""
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Current Password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm New Password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['new_password1'].help_text = ""
        self.fields['new_password2'].help_text = ""
