from datetime import datetime
from io import BytesIO
from weasyprint import HTML

from django.db.models import Sum
from django.template.loader import render_to_string

from foodgram.settings import TEMPLATES_DIR
from recipes.models import RecipeIngredient


def create_shopping_cart(username, ingredients):
    """Создание pdf-файла со списком покупок для загрузки."""

    template_path = f'{TEMPLATES_DIR}/shopping_cart_template.html'

    context = {
        'username': username,
        'ingredients': ingredients,
        'current_date': datetime.today().strftime('%d.%m.%Y'),
    }

    html_string = render_to_string(template_path, context)

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)

    return pdf_file.getvalue()


def get_shopping_cart_ingredients(user):
    """Запрос для получения ингредиентов для списка покупок."""

    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_list_entries=user
    ).order_by(
        'ingredient__name'
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(total_amount=Sum('amount'))

    return ingredients
