from django.contrib.auth.models import AnonymousUser
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from django_filters import CharFilter, FilterSet

from recipes.models import Recipe, Ingredient
from users.models import User


class RecipesFiltering(filters.FilterSet):
    """Фильтр для сортировки выдачи по тегам."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        label='favorites',
    )

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='shopping_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_user_anonimous(self):
        """
        Проверка на анонимность пользователя.
        Если анонимен, избранного у него быть не может,
        показываем ошибку.
        """

        user = self.request.user
        if isinstance(user, AnonymousUser):
            raise ValidationError(
                'Вы не можете фильтровать избранное. '
                'Для такой фильтрации вы должны быть авторизованы.'
            )
        return user

    def get_is_favorited(self, queryset, name, value):
        """Фильтруем избранное."""

        user = self.is_user_anonimous()
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по списку покупок."""

        if value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтрация по имени ингредиента."""
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
