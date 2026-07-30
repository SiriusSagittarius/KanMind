"""URL-Routen der auth_app (Registrierung, Login, E-Mail-Check)."""
from django.urls import path

from .views import EmailCheckView, LoginView, RegistrationView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
]
