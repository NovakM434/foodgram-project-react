***Продуктовый помошник - FOODGRAM***
____
Foodgram - это проект, который создан для того, чтобы люди могли обмениваться рецептами. Пользователь после регистрации может опубликовать свой рецепт, посмотреть уже опубликованные рецепты, подписаться на автора, добавить рецепт в избранное и скачать список покупок, где будут подсчитаны все ингредиенты. 
___
Технологии:
- Python 3.9
 - djangorestframework           3.12.4
- Django                        3.2.22
- djoser                        2.1.0
-   Djoser 2.2.0
-   Gunicorn 20.1.0
 
 API конфигурация:
 
 ПРИМЕРЫ ЗАПРОСОВ

`/api/tags/`  GET - Получение списка всех тегов.

`/api/tags/{id}`  GET - Получение тега по id.

`/api/ingredients/`

GET - Получение списка ингредиентов.

`/api/ingredients/{id}/`  GET - Получение ингредиента по id.

`/api/recipes/`

GET - Получение списка всех рецептов. POST - Добавление рецепта.

`/api/recipes/{id}/`

GET - Получение информации о рецепте по id. PATCH - Обновление рецепта. DELETE - Удаление рецепта.

`/api/recipes/{id}/shopping_cart/`

DELETE - Удаление рецепта из списка покупок. POST - Добавление рецепта в список покупок.

`/api/recipes/download_shopping_cart/`  GET - Cкачать список покупок (PDF)

`/api/recipes/{id}/favorite/`

POST - Добавление рецепта в избранное. DELETE - Удаление рецепта из избранного.

`/api/users/`  GET - Получить список всех пользователей.

`/api/users/`  POST - Добавить нового пользователя.

`/api/users/me/`  GET - Получить данные своей учетной записи

`/api/users/{id}/`  GET - Получить пользователя по id.

`/api/users/subscriptions/`  GET - Список подписок.

`/api/users/subscribe/`

POST - Подписаться на пользователя. DELETE - Отписаться от пользователя.

`/api/users/set_password/`

POST - Изменить пароль.

`/api/auth/token/login/`

POST - Получить токен. DELETE - Удалить токен.

Админка - 
email: apbhueta@yahoo.com
password: 89261280033
Ссылка на проект - http://fooodgram-byroman.gotdns.ch/
