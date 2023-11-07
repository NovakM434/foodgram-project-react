from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных в таблицу Ингредиентов'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.csv', encoding="utf-8") as f:
            for line in f:
                ingredient_csv = line.replace('\n', '').split(',')

                ingredient = Ingredient(name=ingredient_csv[0],
                                        measurement_unit=ingredient_csv[1])
                ingredient.save()
