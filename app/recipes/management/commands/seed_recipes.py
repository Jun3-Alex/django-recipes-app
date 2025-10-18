"""Management command to seed sample recipes."""
from __future__ import annotations

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from recipes.models import Category, Recipe

User = get_user_model()

SAMPLE_RECIPES = [
    {
        "title": "Классическая пицца Маргарита",
        "description": "Вневременная итальянская пицца с хрустящей корочкой, пикантным томатным соусом и свежей моцареллой.",
        "steps": "Приготовить тесто\nНамазать соус\nДобавить сыр\nВыпекать до золотистой корочки",
        "cook_time_min": 30,
        "ingredients": "Тесто для пиццы\nТоматный соус\nСвежая моцарелла\nСвежий базилик\nОливковое масло",
        "categories": ["Итальянская", "Вегетарианская"],
    },
    {
        "title": "Курица, запечённая с лимоном и травами",
        "description": "Сочная запечённая курица с лимоном и ароматными травами — идеальна для воскресного ужина.",
        "steps": "Приправить курицу\nНачинить лимонами\nЗапечь в духовке",
        "cook_time_min": 75,
        "ingredients": "Целая курица\nЛимоны\nЧеснок\nРозмарин\nТимьян",
        "categories": ["Ужин", "Домашняя еда"],
    },
    {
        "title": "Острая тайская лапша",
        "description": "Рисовая лапша, заправленная острым арахисовым соусом и свежими овощами.",
        "steps": "Отварить лапшу\nПриготовить соус\nСмешать с овощами",
        "cook_time_min": 25,
        "ingredients": "Рисовая лапша\nАрахисовое масло\nСоевый соус\nЧили-паста\nОвощная смесь",
        "categories": ["Азиатская", "Острая"],
    },
    {
        "title": "Тост с авокадо и пашот",
        "description": "Кремовый тост с авокадо, украшенный идеально приготовленными яйцами пашот — сытный завтрак.",
        "steps": "Поджарить хлеб\nРазмять авокадо\nСделать яйца пашот\nСобрать блюдо",
        "cook_time_min": 15,
        "ingredients": "Хлеб\nАвокадо\nЯйца\nЛимонный сок\nПерец чили (flakes)",
        "categories": ["Завтрак", "Быстрое блюдо"],
    },
    {
        "title": "Шоколадный фондан",
        "description": "Шоколадные мини-кексы с жидкой сердцевиной — невероятно вкусный десерт.",
        "steps": "Приготовить тесто\nРазлить по формочкам\nКоротко выпечь",
        "cook_time_min": 20,
        "ingredients": "Тёмный шоколад\nМасло\nСахар\nЯйца\nМука",
        "categories": ["Десерт", "Шоколад"],
    },
]

IMAGE_NAMES = [
    "classic_margherita.png",
    "lemon_herb_roasted_chicken.png",
    "spicy_thai_noodle_bowl.png",
    "avocado_toast_poached_eggs.png",
    "chocolate_lava_cake.png",
]


class Command(BaseCommand):
    help = "Seed the database with sample recipes."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@example.com"})
        if created or not user.has_usable_password():
            user.set_password("demo1234")
            user.save()

        seed_images_dir = Path(__file__).resolve().parent / "seed_images"

        for image_name, recipe_data in zip(IMAGE_NAMES, SAMPLE_RECIPES):
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
                image_path = seed_images_dir / image_name
                if image_path.exists():
                    with image_path.open("rb") as image_file:
                        recipe.image.save(image_name, ContentFile(image_file.read()), save=False)
            recipe.author = user
            recipe.description = recipe_data["description"]
            recipe.steps = recipe_data["steps"]
            recipe.cook_time_min = recipe_data["cook_time_min"]
            recipe.ingredients = recipe_data["ingredients"]
            recipe.save()
            recipe.categories.set(categories)

        self.stdout.write(self.style.SUCCESS("Seeded sample recipes."))