from rest_framework.pagination import PageNumberPagination


class PageNumberPagination(PageNumberPagination):
    """Кастомный класс для пагинации"""

    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 20
