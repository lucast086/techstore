"""URL configuration for the users app."""

from django.urls import path
from users.views import LoginView, LogoutView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
