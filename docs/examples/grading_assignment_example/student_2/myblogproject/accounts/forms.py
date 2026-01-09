from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms

# Custom user registration form extending the default UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

# Custom user profile update form extending the default UserChangeForm
class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    #last_login = forms.CharField()
    #date_joined = forms.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')