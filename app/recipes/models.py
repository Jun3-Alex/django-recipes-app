"""Models for the recipes application."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class Category(models.Model):
    """Recipe categorisation model."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RecipeCategory(models.Model):
    """Explicit through model between recipes and categories."""

    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("recipe", "category")
        verbose_name = "Recipe category"
        verbose_name_plural = "Recipe categories"

    def __str__(self) -> str:
        return f"{self.recipe.title} → {self.category.name}"


class Recipe(models.Model):
    """Represents a cookable recipe."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    steps = models.TextField()
    cook_time_min = models.PositiveIntegerField()
    image = models.ImageField(upload_to="recipes/")
    ingredients = models.TextField(help_text="List ingredients separated by commas or line breaks.")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    categories = models.ManyToManyField(Category, through=RecipeCategory, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title