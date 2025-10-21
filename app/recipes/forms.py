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
        label="Изображение",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "file-input",
                "accept": "image/jpeg,image/png,image/gif",
            }
        ),
        help_text="Загрузите фотографию блюда.",
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label="Категории",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "checkbox-list",
            }
        ),
        required=False,
        help_text="Выберите категории, которые подходят рецепту.",
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
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Введите запоминающееся название рецепта",
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "placeholder": "Опишите блюдо и чем оно особенное",
                    "rows": 3,
                }
            ),
            "steps": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "placeholder": "Перечислите шаги приготовления по порядку",
                    "rows": 6,
                }
            ),
            "cook_time_min": forms.NumberInput(
                attrs={
                    "class": "input",
                    "min": 0,
                    "placeholder": "Общее время приготовления в минутах",
                }
            ),
            "ingredients": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "placeholder": "Перечислите ингредиенты с количеством",
                    "rows": 4,
                }
            ),
        }
        labels = {
            "title": "Название",
            "description": "Описание",
            "steps": "Шаги приготовления",
            "cook_time_min": "Время приготовления (мин)",
            "ingredients": "Ингредиенты",
        }
        help_texts = {
            "ingredients": "Перечисляйте ингредиенты через запятую или с новой строки.",
        }

    def clean_image(self) -> Any:
        image = self.cleaned_data.get("image")
        if not image:
            if self.instance and self.instance.pk and self.instance.image:
                return self.instance.image
            raise ValidationError("Для рецепта необходимо изображение.")

        content_type = getattr(image, "content_type", None)
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Неподдерживаемый тип файла. Загрузите JPEG, PNG или GIF.")

        size = getattr(image, "size", None)
        if size is None:
            return image

        max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            raise ValidationError(f"Файл слишком большой (>{MAX_IMAGE_SIZE_MB} МБ).")
        return image