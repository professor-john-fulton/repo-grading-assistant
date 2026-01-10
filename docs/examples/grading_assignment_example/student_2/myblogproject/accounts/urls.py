from django.urls import path
from .views import RegsterView, ProfileView, PasswordsChangeView
from . import views

# Define the URL patterns for the accounts app
urlpatterns = [
    path('register/', RegsterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    #path('password/', auth_views.PasswordChangeView.as_view(template_name='registration/password.html', success_url=reverse_lazy('profile')), name='change_password'),
    #path('password/', auth_views.PasswordChangeView.as_view(template_name='registration/password.html'), name='change_password'),
    path('password/', PasswordsChangeView.as_view(template_name='registration/password.html'), name='change_password'),
    path('password_changed', views.password_changed, name='password_changed'),
]

