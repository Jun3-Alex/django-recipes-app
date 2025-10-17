# Generated manually for initial migration
from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("steps", models.TextField()),
                ("cook_time_min", models.PositiveIntegerField()),
                ("image", models.ImageField(upload_to="recipes/")),
                (
                    "ingredients",
                    models.TextField(help_text="List ingredients separated by commas or line breaks."),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RecipeCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("added_on", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="recipes.category"),
                ),
                (
                    "recipe",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="recipes.recipe"),
                ),
            ],
            options={
                "verbose_name": "Recipe category",
                "verbose_name_plural": "Recipe categories",
                "unique_together": {("recipe", "category")},
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="categories",
            field=models.ManyToManyField(related_name="recipes", through="recipes.RecipeCategory", to="recipes.category"),
        ),
    ]