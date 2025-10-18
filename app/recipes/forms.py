"""Forms for creating and editing recipes."""
from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Recipe

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_IMAGE_SIZE_MB = 5


class RecipeForm(forms.ModelForm):
    """Model form for creating and editing recipes."""

    image = forms.FileField(
        widget=forms.ClearableFileInput,
        help_text="Upload a recipe photo.",
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select categories that best fit the recipe.",
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "description",
            "steps",
            "cook_time_min",
            "image",
            "ingredients",
            "categories",
        ]

    def clean_image(self) -> Any:
        image = self.cleaned_data.get("image")
        if not image:
            if self.instance and self.instance.pk and self.instance.image:
                return self.instance.image
            raise ValidationError("An image is required for recipes.")

        content_type = getattr(image, "content_type", None)
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Unsupported image type. Please upload JPEG, PNG, or GIF.")

        size = getattr(image, "size", None)
        if size is None:
            return image

        max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            raise ValidationError(f"Image file too large (>{MAX_IMAGE_SIZE_MB} MB).")
        return image