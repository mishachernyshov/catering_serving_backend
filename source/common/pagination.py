from rest_framework.pagination import PageNumberPagination as DrfPageNumberPagination


class PageNumberPagination(DrfPageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 40
    max_page_size = 50
