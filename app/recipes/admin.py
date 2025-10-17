"""Admin registrations for recipes app."""
from __future__ import annotations

from django.contrib import admin

from .models import Category, Recipe, RecipeCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class RecipeCategoryInline(admin.TabularInline):
    model = RecipeCategory
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "cook_time_min", "created_at")
    list_filter = ("categories",)
    search_fields = ("title", "description", "ingredients")
    inlines = [RecipeCategoryInline]


@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    list_display = ("recipe", "category", "added_on")
    list_filter = ("category", "added_on")
    search_fields = ("recipe__title", "category__name")