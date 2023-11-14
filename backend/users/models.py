from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.validators import validate_username

FIRST_CONSTANT = 150
SECOND_CONSTANT = 254


class User(AbstractUser):

    email = models.EmailField(
        max_length=SECOND_CONSTANT,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Эл. почта',
        help_text='Введите электронную почту'
    )

    username = models.CharField(
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимый символ в username'
            ), validate_username
        ),
        max_length=FIRST_CONSTANT,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Пользователь',
        help_text='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=FIRST_CONSTANT,
        blank=False,
        verbose_name='Имя',
        help_text='Введите имя'
    )
    last_name = models.CharField(
        max_length=FIRST_CONSTANT,
        blank=False,
        verbose_name='Фамилия',
        help_text='Введите фамилию'

    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def get_recipes_count(self):
        return self.recipes.count()

    def get_followers_count(self):
        return self.author.count()

    get_recipes_count.short_description = 'Количество рецептов'
    get_followers_count.short_description = 'Количество подписчиков'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'follower'),
                name='unique_following'
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_follow",
                check=~models.Q(follower=models.F("author")),
            ),
        )
        ordering = ('author',)

    def __str__(self):
        return f'Подписка {self.follower} на {self.author}'
