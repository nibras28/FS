from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User  # Use Django's built-in User model
        fields = ('username', 'email', 'password')


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Invalid username or password. Please try again.",  # Customize the error message here
    }
