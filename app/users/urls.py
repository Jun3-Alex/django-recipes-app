"""URL patterns for the users app."""
from __future__ import annotations

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
]