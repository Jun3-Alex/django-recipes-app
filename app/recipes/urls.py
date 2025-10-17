"""URL routes for recipes app."""
from __future__ import annotations

from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("recipes/<int:pk>/", views.RecipeDetailView.as_view(), name="detail"),
    path("recipes/create/", views.RecipeCreateView.as_view(), name="create"),
    path("recipes/<int:pk>/edit/", views.RecipeUpdateView.as_view(), name="edit"),
    path("api/random/", views.random_recipe_json, name="random-json"),
]