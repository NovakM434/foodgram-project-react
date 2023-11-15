from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """
    Кастомная пагинация для отображения количества
    элементов, равного значению параметра limit в запросе.
    """
    page_size_query_param = 'limit'
    page_size = 6
