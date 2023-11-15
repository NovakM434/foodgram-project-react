from django.urls import path, include
from rest_framework import routers

from api.views import (RecipesViewSet, TagsViewSet, UsersViewSet,
                       IngredientsViewSet)

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet)
router.register('users', UsersViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
