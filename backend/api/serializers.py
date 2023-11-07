from collections import Counter

from djoser.serializers import (UserSerializer as DjoserUserSerializer,
                                UserSerializer)
from rest_framework import status
from django.core.validators import RegexValidator
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Recipe, Tags, Ingredient, Favorite,
                            RecipeIngredient, ShoppingList)
from users.models import User, Follow


class SignUpSerializer(DjoserUserSerializer):
    """Сериализатор регистрации пользователя."""

    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+-]+$')]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'password']
        read_only_fields = ['id', ]

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" зарезервировано в системе'
            )
        return data


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для работы с User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        """Подписан ли пользователь на автора."""

        user = self.context.get('request').user
        print(user, user.is_authenticated)
        if user and user.is_authenticated:
            return user.follower.filter(author=object).exists()
        return False


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'ingredient')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    author = serializers.StringRelatedField()
    author = SignUpSerializer()
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipes_ingredients')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'cooking_time', 'text',
                  'ingredients', 'image', 'name')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с эндпоинтом 'me'."""

    class Meta:
        model = User
        fields = "__all__"


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['id']
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном'
            ),
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "__all__"


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('author', 'follower')
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'follower'),
                message='Подписка на автора уже оформлена'
            ),
        )

        def validate(self, data):
            """Проверка на подписку на самого себя."""

            author_id = data['author'].id
            follower_id = data['follower'].id

            if author_id == follower_id:
                raise ValidationError(
                    'Нельзя подписаться на самого себя'
                )

            data = super().validate(data)

            return data


class FollowingSerializer(UserSerializer):
    """Сериализатор для вывода информации о подписках."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    @staticmethod
    def get_recipes(object):
        """Получаем рецепты с уменьшенным набором полей."""

        return ShortRecipeSerializer(
            object.recipes.all()[:10], many=True
        ).data

    @staticmethod
    def get_recipes_count(object):
        """Получение количества рецептов."""

        return object.recipes.count()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipes_ingredients',
    )
    tags = TagsSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )
    is_favorited = serializers.BooleanField(
        read_only=True, default=False
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Валидация на наличие ингредиентов и тегов в рецепте."""
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        image = data.get('image')

        if not ingredients:
            raise serializers.ValidationError("Ingredients field is required.")

        if not tags:
            raise serializers.ValidationError("Tags field is required.")

        if not image:
            raise serializers.ValidationError("Image field is required")

        return data

    @staticmethod
    def validate_ingredients(ingredients):
        """Проверка ингредиентов на уникальность и минимальное количество."""

        ingredients_lst = [ingredient.get('id') for ingredient in ingredients]
        ingredient_counter = Counter(ingredients_lst)

        if any(count > 1 for count in ingredient_counter.values()):
            raise ValidationError(
                [{'ingredients': ['Ингредиенты не должны повторяться.']}]
            )

        if any(int(ingredient.get('amount')) < 1 for ingredient in
               ingredients):
            raise ValidationError(
                [{
                    'ingredients':
                        ['Количество ингредиента не может быть меньше 1']
                }]
            )

        return ingredients

    @staticmethod
    def validate_tags(tags):
        """Проверка тэгов на уникальность."""

        existing_tags = [tag.name for tag in Tags.objects.all()]
        received_tags = [tag.name for tag in tags]

        if not tags:
            raise ValidationError(
                'Нужно выбрать хотя бы один тэг'
            )

        for tag in received_tags:
            if tag not in existing_tags:
                raise ValidationError(
                    f'Тэг {tag} не существует'
                )

        if len(set(tags)) != len(tags):
            raise ValidationError(
                'Теги должны быть уникальными'
            )

        return tags

    def validate_cooking_time(self, data):
        """Проверка времени приготовления."""

        cooking_time = self.initial_data.get('cooking_time')

        if int(cooking_time) < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше 1 минуты'
            )

        return data

    @staticmethod
    def add_ingredients(ingredients, recipe):
        """Добавление ингредиентов."""

        recipe.ingredients.clear()

        ingredient_ids = [item['id'] for item in ingredients]
        db_ingredients = Ingredient.objects.in_bulk(ingredient_ids)

        recipe_ingredients = [
            RecipeIngredient(
                ingredient=db_ingredients[item['id']],
                recipe=recipe,
                amount=item['amount']
            )
            for item in ingredients
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        """Изменение рецепта автором."""
        data = validated_data.copy()
        # Проверяем, был ли указан ингредиент.
        if 'ingredient' in data:
            try:
                RecipeIngredient.objects.get(recipe=instance,
                                             ingredient=data['ingredient'])
            # Если ингредиента не существует, возвращаем статус 400.
            except RecipeIngredient.DoesNotExist:
                return Response(
                    {'detail': 'Указанный ингредиент не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        self.add_ingredients(ingredients_data, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Выбор типа сериализатора для чтения и записи рецепта."""

        return RecipesReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в список покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок'
            ),
        )
