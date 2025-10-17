"""Views for the recipes application."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import RecipeForm
from .models import Recipe


class HomeView(ListView):
    """Displays five random recipes on the homepage."""

    model = Recipe
    context_object_name = "recipes"
    template_name = "recipes/home.html"

    def get_queryset(self):  # type: ignore[override]
        count = Recipe.objects.count()
        if count <= 5:
            return Recipe.objects.all()
        # Use database-level random ordering limited to five items for efficiency.
        return Recipe.objects.order_by("?")[:5]


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/detail.html"
    context_object_name = "recipe"


class RecipeAuthorRequiredMixin(UserPassesTestMixin):
    """Ensure the user is the author of the recipe."""

    def test_func(self) -> bool:
        recipe = self.get_object()  # type: ignore[attr-defined]
        return recipe.author == self.request.user

    def handle_no_permission(self):  # type: ignore[override]
        messages.error(self.request, "You do not have permission to modify this recipe.")
        return redirect("recipes:detail", pk=self.get_object().pk)  # type: ignore[attr-defined]


class RecipeCreateView(LoginRequiredMixin, View):
    template_name = "recipes/form.html"
    form_class = RecipeForm

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class()
        return render(request, self.template_name, {"form": form, "title": "Create recipe"})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()
            messages.success(request, "Recipe created successfully!")
            return redirect("recipes:detail", pk=recipe.pk)
        return render(request, self.template_name, {"form": form, "title": "Create recipe"})


class RecipeUpdateView(LoginRequiredMixin, RecipeAuthorRequiredMixin, DetailView):
    model = Recipe
    template_name = "recipes/form.html"
    form_class = RecipeForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        recipe = self.get_object()
        form = self.form_class(instance=recipe)
        return render(request, self.template_name, {"form": form, "title": "Edit recipe", "recipe": recipe})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        recipe = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, "Recipe updated successfully!")
            return redirect("recipes:detail", pk=recipe.pk)
        return render(request, self.template_name, {"form": form, "title": "Edit recipe", "recipe": recipe})


def random_recipe_json(request: HttpRequest) -> JsonResponse:
    """Return a random recipe payload as JSON."""

    recipe = Recipe.objects.order_by("?").first()
    if not recipe:
        return JsonResponse({"error": "No recipes available"}, status=404)
    return JsonResponse(
        {
            "id": recipe.pk,
            "title": recipe.title,
            "description": recipe.description,
            "cook_time_min": recipe.cook_time_min,
        }
    )