# Generated by Django 3.2.22 on 2023-11-06 15:47

import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранное',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название ингредиента', max_length=150, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(help_text='Введите единицу измерения', max_length=50, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', models.ImageField(help_text='Загрузите изображение', upload_to='recipes/images/', verbose_name='Изображения')),
                ('text', models.TextField(help_text='Введите описание рецепта', verbose_name='Описание')),
                ('cooking_time', models.IntegerField(help_text='Укажите время приготовления в минутах', validators=[django.core.validators.MinValueValidator(limit_value=1, message='Время приготовления не может быть меньше 1 минуты')], verbose_name='Время приготовления (мин.)')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Время публикации')),
                ('author', models.ForeignKey(help_text='Укажите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('favorited_by', models.ManyToManyField(help_text='Рецепты в избранном', related_name='favorites_recipes', through='recipes.Favorite', to=settings.AUTH_USER_MODEL, verbose_name='Избранные рецепты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название тэга', max_length=300, unique=True, verbose_name='Название Тэга')),
                ('color', colorfield.fields.ColorField(default='#FF0000', help_text='Цвет в HEX (Например, #00FF00)', image_field=None, max_length=7, samples=None, unique=True, verbose_name='Цвет')),
                ('slug', models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message='В слаге содержится недопустимый символ', regex='^[-a-zA-Z0-9_]+$')])),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to='recipes.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(help_text='Выберите пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Список покупок',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('ingredient', models.ForeignKey(help_text='Выберите ингредиент', on_delete=django.db.models.deletion.CASCADE, related_name='recipes_ingredients', to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(help_text='Укажите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipes_ingredients', to='recipes.recipe', verbose_name='Рецепт')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='shopping_list_entries',
            field=models.ManyToManyField(help_text='Рецепты, добавленные в список покупок', related_name='shopping_list_recipes', through='recipes.ShoppingList', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите подходящие тэги', related_name='recipes', to='recipes.Tags', verbose_name='Тэг'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(help_text='Выберите пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_recipe_shopping_list'),
        ),
    ]