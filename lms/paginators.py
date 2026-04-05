from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """Пагинатор для курсов"""
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальное количество элементов на странице


class LessonPaginator(PageNumberPagination):
    """Пагинатор для уроков"""
    page_size = 15  # Количество элементов на странице по умолчанию
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальное количество элементов на странице
