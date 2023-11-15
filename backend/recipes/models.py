from colorfield.fields import ColorField

from django.core.validators import (MinValueValidator, MaxValueValidator)
from django.db import models

from api.constants import THIRD_CONSTANT
from users.models import User


class Tags(models.Model):
    name = models.CharField(
        max_length=THIRD_CONSTANT,
        unique=True,
        verbose_name='Название Тэга',
        help_text='Введите название тэга'
    )
    color = ColorField(
        default='#FF0000',
        max_length=7,
        unique=True,
        verbose_name='Цвет',
        help_text='Цвет в HEX (Например, #00FF00)'
    )
    slug = models.CharField(max_length=THIRD_CONSTANT)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.slug}'


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        max_length=THIRD_CONSTANT,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=THIRD_CONSTANT,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        help_text='Укажите автора рецепта'
    )
    name = models.CharField(max_length=THIRD_CONSTANT)
    image = models.ImageField(
        null=False,
        upload_to='recipes/images/',
        verbose_name='Изображения',
        help_text='Загрузите изображение')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tags,
        blank=False,
        related_name='recipes',
        verbose_name='Тэг',
        help_text='Выберите подходящие тэги'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Описание',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Время приготовления не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                limit_value=600,
                message='Время приготовления не может быть больше 10 часов'
            )
        ),
        verbose_name='Время приготовления (мин.)',
        help_text='Укажите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации'
    )
    favorited_by = models.ManyToManyField(User, through='Favorite',
                                          related_name='favorites_recipes',
                                          verbose_name='Избранные рецепты',
                                          help_text='Рецепты в избранном')

    shopping_list_entries = models.ManyToManyField(
        User,
        through='ShoppingList',
        related_name='shopping_list_recipes',
        verbose_name='Список покупок',
        help_text='Рецепты, добавленные в список покупок'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes_ingredients',
        help_text='Укажите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipes_ingredients',
        help_text='Выберите ингредиент'
    )
    amount = models.PositiveIntegerField()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return (
            f'Ингредиенты для "{self.recipe}": {self.ingredient} - '
            f'{self.amount}'
        )


class FavoriteAndShoppingAbstarctModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        abstract = True


class Favorite(FavoriteAndShoppingAbstarctModel):
    """"Класс для избранного"""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('id',)

    def __str__(self):
        return f"Пользователь {self.user} добавил {self.recipe} в избранное"


class ShoppingList(FavoriteAndShoppingAbstarctModel):
    """Класс для списка покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_list'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок'
