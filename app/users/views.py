"""Views for user management."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup(request: HttpRequest) -> HttpResponse:
    """Render and process the user signup form."""

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("recipes:home")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})