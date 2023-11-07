from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.validators import validate_username


class User(AbstractUser):

    ADMIN = 'admin'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (USER, 'Пользователь'),
    ]

    email = models.EmailField(
        max_length=254,
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
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Пользователь',
        help_text='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
        help_text='Введите имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
        help_text='Введите фамилию'

    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        max_length=150,
        blank=True,
        verbose_name='Роль',
        help_text='Выберите роль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email',
            ),
        )
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN


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
        )
        ordering = ('id',)

    def __str__(self):
        return f'Подписка {self.follower} на {self.author}'
