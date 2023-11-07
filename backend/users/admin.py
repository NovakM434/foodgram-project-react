from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, Follow

admin.site.site_title = 'Foodgram'
admin.site.site_header = 'Проект "Foodgram"'


@admin.register(User)
class UserAdmin(UserAdmin):
    """Приложение users."""

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    list_display_links = ('username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    ordering = ('id',)
    empty_value_display = '-Пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Подписки."""

    list_display = ('author', 'follower')
    list_display_links = ('author', 'follower')
    list_filter = ('author', 'follower')
    ordering = ('author',)
