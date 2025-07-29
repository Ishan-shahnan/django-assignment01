from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Event, Participant, Category

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., Annual Tech Conference'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'rows': 4,
                'placeholder': 'Brief description of the event...'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., Grand Exhibition Hall'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm'
            })
        }
    

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., Jane Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., jane.doe@example.com'
            }),
            'events': forms.SelectMultiple(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if Participant.objects.filter(email=email).exists():
                raise ValidationError("A participant with this email already exists.")
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        return name.strip()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., Conference'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'rows': 3,
                'placeholder': 'e.g., Events focused on knowledge sharing'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Category name must be at least 2 characters long.")
            
            # Check for duplicate names (case-insensitive)
            if Category.objects.filter(name__iexact=name).exists():
                raise ValidationError("A category with this name already exists.")
        
        return name 