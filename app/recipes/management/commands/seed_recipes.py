"""Management command to seed sample recipes."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from recipes.models import Category, Recipe

User = get_user_model()

SAMPLE_RECIPES = [
    {
        "title": "Classic Margherita Pizza",
        "description": "A timeless Italian pizza with a crispy crust, tangy tomato sauce, and fresh mozzarella.",
        "steps": "Prepare dough\nSpread sauce\nAdd cheese\nBake until golden",
        "cook_time_min": 30,
        "ingredients": "Pizza dough\nTomato sauce\nFresh mozzarella\nFresh basil\nOlive oil",
        "categories": ["Italian", "Vegetarian"],
    },
    {
        "title": "Lemon Herb Roasted Chicken",
        "description": "Juicy roasted chicken infused with lemon and herbs, perfect for Sunday dinner.",
        "steps": "Season chicken\nStuff with lemons\nRoast in oven",
        "cook_time_min": 75,
        "ingredients": "Whole chicken\nLemons\nGarlic\nRosemary\nThyme",
        "categories": ["Dinner", "Comfort Food"],
    },
    {
        "title": "Spicy Thai Noodle Bowl",
        "description": "Rice noodles tossed with a spicy peanut sauce and fresh vegetables.",
        "steps": "Cook noodles\nPrepare sauce\nToss with veggies",
        "cook_time_min": 25,
        "ingredients": "Rice noodles\nPeanut butter\nSoy sauce\nChili paste\nMixed vegetables",
        "categories": ["Asian", "Spicy"],
    },
    {
        "title": "Avocado Toast with Poached Eggs",
        "description": "Creamy avocado toast topped with perfectly poached eggs for a hearty breakfast.",
        "steps": "Toast bread\nMash avocado\nPoach eggs\nAssemble",
        "cook_time_min": 15,
        "ingredients": "Bread\nAvocados\nEggs\nLemon juice\nChili flakes",
        "categories": ["Breakfast", "Quick"],
    },
    {
        "title": "Chocolate Lava Cake",
        "description": "Decadent molten chocolate cakes with gooey centers.",
        "steps": "Prepare batter\nFill ramekins\nBake briefly",
        "cook_time_min": 20,
        "ingredients": "Dark chocolate\nButter\nSugar\nEggs\nFlour",
        "categories": ["Dessert", "Chocolate"],
    },
]

PLACEHOLDER_IMAGE = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\x0b\x0e\x02\xb5\x00\x00\x00\x00IEND\xaeB`\x82"
)


class Command(BaseCommand):
    help = "Seed the database with sample recipes."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@example.com"})
        if created or not user.has_usable_password():
            user.set_password("demo1234")
            user.save()

        for recipe_data in SAMPLE_RECIPES:
            category_names = recipe_data["categories"]
            categories = [
                Category.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" ", "-")})[0]
                for name in category_names
            ]

            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data["title"],
                defaults={
                    "author": user,
                    "description": recipe_data["description"],
                    "steps": recipe_data["steps"],
                    "cook_time_min": recipe_data["cook_time_min"],
                    "ingredients": recipe_data["ingredients"],
                },
            )

            if created or not recipe.image:
                recipe.image.save("placeholder.png", ContentFile(PLACEHOLDER_IMAGE), save=False)
            recipe.author = user
            recipe.description = recipe_data["description"]
            recipe.steps = recipe_data["steps"]
            recipe.cook_time_min = recipe_data["cook_time_min"]
            recipe.ingredients = recipe_data["ingredients"]
            recipe.save()
            recipe.categories.set(categories)

        self.stdout.write(self.style.SUCCESS("Seeded sample recipes."))