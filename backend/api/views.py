from io import BytesIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from django.db.models import Exists, OuterRef

from users.models import Follow, User
from .filters import RecipesFiltering, IngredientFilter
from recipes.models import (Ingredient, Favorite, Tags, Recipe, ShoppingList)
from .paginaton import LimitPagination
from .permissions import IsAuthor, IsAdmin
from .serializers import (TagsSerializer, IngredientsSerializer,
                          FavoriteSerializer, ShortRecipeSerializer,
                          FollowSerializer, FollowingSerializer,
                          UserSerializer, RecipesReadSerializer,
                          RecipesWriteSerializer, ShoppingListSerializer)
from .utils import get_shopping_cart_ingredients, create_shopping_cart


class UsersViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination
    permission_classes = (AllowAny, )

    @action(methods=['get'], detail=False, url_path='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UserSerializer)
    def get_me(self, request):
        """Получение информации о себе."""
        serializer = UserSerializer(
            instance=request.user,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='subscribe',
            permission_classes=(IsAuthenticated,),
            serializer_class=FollowSerializer)
    def follow(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == "DELETE":
            del_follow, _ = Follow.objects.filter(
                author=author,
                follower=request.user).delete()
            if del_follow:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FollowSerializer(data={'author': author.id,
                                            'follower': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated,),
            serializer_class=FollowSerializer)
    def sub_list(self, request):
        user = request.user
        queryset = User.objects.filter(author__follower=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowingSerializer(pages,
                                         context={'request': request},
                                         many=True)
        return self.get_paginated_response(serializer.data)


class BaseRecipeMixin:
    @staticmethod
    def add_or_remove_to_favorites_or_cart(
            request, pk, model_class, serializer_class
    ):

        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'DELETE':
            del_count, _ = model_class.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            if del_count:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action_serializer = ShortRecipeSerializer(recipe)
        return Response(
            action_serializer.data, status=status.HTTP_201_CREATED
        )


class RecipesViewSet(viewsets.ModelViewSet, BaseRecipeMixin):
    """Вьюсет для создания объектов класса Recipe."""

    serializer_class = RecipesWriteSerializer
    permission_classes = ((IsAuthor | IsAdmin),)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFiltering
    pagination_class = LimitPagination

    def get_queryset(self):
        """
        Получение оптимизированного queryset
        с аннотациями и подзапросами.
        """

        if self.request.user.is_authenticated:
            queryset = Recipe.objects.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=self.request.user,
                    recipe_id=OuterRef('pk'),
                )),
                is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                    user=self.request.user,
                    recipe_id=OuterRef('pk'),
                ))
            ).select_related('author')

            return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite',
            permission_classes=(IsAuthenticated,),
            serializer_class=FavoriteSerializer)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            del_favorite, _ = Favorite.objects.filter(user=request.user,
                                                      recipe=recipe).delete()
            if del_favorite:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action_serializer = ShortRecipeSerializer(recipe)
        return Response(action_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def manage_shopping_cart(self, request, pk):
        """
        Позволяет текущему пользователю добавлять/удалять рецепты
        в список покупок.
        """

        return self.add_or_remove_to_favorites_or_cart(
            request, pk, ShoppingList, ShoppingListSerializer
        )

    @action(
        detail=False, methods=['GET'], url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок, если он есть."""

        if not request.user.shopping_list.exists():
            return Response({'errors': 'Корзина пуста'},
                            status=status.HTTP_400_BAD_REQUEST)

        username = request.user.username
        ingredients = get_shopping_cart_ingredients(request.user)
        pdf_file_data = create_shopping_cart(username, ingredients)
        response = FileResponse(BytesIO(pdf_file_data),
                                content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = f'attachment; filename="{username}_download_list.pdf"'
        return response

    def get_serializer_class(self):
        """Выбор сериализатора для чтения рецепта и редактирования."""

        if self.request.method == 'GET':
            return RecipesReadSerializer
        return RecipesWriteSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_field = ('name',)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('name',)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
