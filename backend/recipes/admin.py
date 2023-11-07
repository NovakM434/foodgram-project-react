from django.contrib import admin
from django.utils.html import format_html

from recipes.models import (Tags, RecipeIngredient, Recipe)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    ordering = ('id',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-Пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = ('id', 'recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')
    ordering = ('id',)
    empty_value_display = '-Пусто-'


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    def show_image(self, object):
        if object.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; '
                'object-fit: cover;" />', object.image.url
            )
        return 'Нет изображения'

    show_image.short_description = 'Изображение'

    def show_tags(self, object):
        return '\n'.join((tag.name for tag in object.tags.all()))

    show_tags.short_description = 'Тэги'

    def show_ingredients(self, object):
        return '\n'.join(
            (ingredient.name for ingredient in object.ingredients.all())
        )

    show_ingredients.short_description = 'Используемые ингредиенты'

    def show_favorite(self, object):
        return object.favorites.all().count()

    show_favorite.short_description = 'В избранном'

    list_display = (
        'id', 'name', 'author', 'show_tags', 'show_ingredients',
        'text', 'cooking_time', 'pub_date', 'show_image', 'show_favorite'
    )
    search_fields = ('author__username', 'name')
    list_filter = ('author__username', 'name', 'tags')

    ordering = ('id',)
    empty_value_display = '-Пусто-'
    inlines = (
        IngredientsInLine,
    )
