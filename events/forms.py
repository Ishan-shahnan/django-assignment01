from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Event, Participant, Category
from users.models import CustomUser


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
            'image': forms.FileInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'accept': 'image/*'
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
            # email exists?
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

            #duplicate names
            if Category.objects.filter(name__iexact=name).exists():
                raise ValidationError("A category with this name already exists.")
        return name


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., johndoe123'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., John'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'e.g., john.doe@example.com'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'Enter password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
                'placeholder': 'Confirm password'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # password
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
            'placeholder': 'Confirm password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip()
            if len(first_name) < 2:
                raise ValidationError("First name must be at least 2 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip()
            if len(last_name) < 2:
                raise ValidationError("Last name must be at least 2 characters long.")
        return last_name


class SignInForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm',
            'placeholder': 'Password'
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        print(f'Username before cleaning: {username}')
        if username:
            username = username.strip()
            # if len(username) < 2:
            #     raise ValidationError("Username must be at least 2 characters long.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        print(f'Password before cleaning: {password}')
        if password:
            password = password.strip()
            # if len(password) < 6:
            #     raise ValidationError("Password must be at least 6 characters long.")
        return password


# RBA access
class AssignRoleForm(forms.Form):
    ROLE_CHOICES = [
        ('', 'Select Role'),
        ('Admin', 'Admin'),
        ('Organizer', 'Organizer'),
        ('Participant', 'Participant'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-400 focus:border-transparent shadow-sm'
        })
    )

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise ValidationError("Please select a role.")
        return role


class CreateGroupForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'flex-grow p-3 border border-red-300 rounded-lg focus:outline-none focus:ring-4 focus:ring-red-400 focus:border-transparent shadow-sm',
            'placeholder': 'New group name',
            'required': True
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Group name must be at least 2 characters long.")
        
            from django.contrib.auth.models import Group
            if Group.objects.filter(name__iexact=name).exists():
                raise ValidationError("A group with this name already exists.")
        return name
