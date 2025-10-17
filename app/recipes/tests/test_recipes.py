"""Tests for recipes application."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from recipes.models import Category, Recipe, RecipeCategory

User = get_user_model()


def create_test_image(name: str = "test.png") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\x0b\x0e\x02\xb5\x00\x00\x00\x00IEND\xaeB`\x82", content_type="image/png")


class RecipeModelTests(TestCase):
    """Tests for recipe models."""

    def setUp(self):
        self.user = User.objects.create_user("tester", "tester@example.com", "password")

    def test_recipe_creation_with_categories(self):
        category = Category.objects.create(name="Dinner", slug="dinner")
        recipe = Recipe.objects.create(
            title="Test Recipe",
            description="Delicious meal",
            steps="Do stuff",
            cook_time_min=45,
            image=create_test_image(),
            ingredients="Ingredient 1\nIngredient 2",
            author=self.user,
        )
        RecipeCategory.objects.create(recipe=recipe, category=category)
        self.assertEqual(recipe.categories.count(), 1)
        self.assertEqual(recipe.categories.first(), category)


class HomePageTests(TestCase):
    """Tests for the home page view."""

    def setUp(self):
        self.user = User.objects.create_user("tester", "tester@example.com", "password")
        category = Category.objects.create(name="Breakfast", slug="breakfast")
        for index in range(7):
            recipe = Recipe.objects.create(
                title=f"Recipe {index}",
                description="Yummy",
                steps="Cook",
                cook_time_min=10,
                image=create_test_image(f"image{index}.png"),
                ingredients="Ingredients",
                author=self.user,
            )
            recipe.categories.add(category)

    def test_home_page_limits_to_five_recipes(self):
        response = self.client.get(reverse("recipes:home"))
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.context["recipes"]), 5)


class RecipeAccessTests(TestCase):
    """Tests for access control on recipe views."""

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("author", "author@example.com", "password")
        self.other_user = User.objects.create_user("other", "other@example.com", "password")
        self.recipe = Recipe.objects.create(
            title="Author's Recipe",
            description="Tasty",
            steps="Cook",
            cook_time_min=20,
            image=create_test_image(),
            ingredients="Things",
            author=self.author,
        )

    def test_create_view_requires_authentication(self):
        response = self.client.get(reverse("recipes:create"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_authenticated_user_can_create_recipe(self):
        self.client.login(username="author", password="password")
        image = create_test_image("new.png")
        response = self.client.post(
            reverse("recipes:create"),
            {
                "title": "New Recipe",
                "description": "Tasty",
                "steps": "Step 1",
                "cook_time_min": 15,
                "image": image,
                "ingredients": "List",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recipe.objects.filter(title="New Recipe").exists())

    def test_only_author_can_edit_recipe(self):
        self.client.login(username="other", password="password")
        response = self.client.get(reverse("recipes:edit", args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("recipes:detail", args=[self.recipe.pk]), response.url)

        self.client.logout()
        self.client.login(username="author", password="password")
        response = self.client.post(
            reverse("recipes:edit", args=[self.recipe.pk]),
            {
                "title": "Updated Title",
                "description": "Updated",
                "steps": "Steps",
                "cook_time_min": 25,
                "image": create_test_image("edit.png"),
                "ingredients": "Ingredients",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Updated Title")