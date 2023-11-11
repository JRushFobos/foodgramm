import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Запуск импорта ингредиентов")
        file_name = "ingredients.csv"
        model = Ingredient
        try:
            with open(
                "recipes/data/ingredients.csv", encoding="utf-8"
            ) as csvfile:
                reader = csv.DictReader(csvfile)
                model.objects.bulk_create(model(**data) for data in reader)
        except FileNotFoundError:
            raise CommandError(f"Файл {file_name} не найден")
        else:
            print("Ингридиенты загружены!")
