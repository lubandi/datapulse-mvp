from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

class DataPulsePagination(LimitOffsetPagination):
    """
    Custom pagination to match the original FastAPI response shapes.
    Uses 'skip' instead of 'offset' and wraps data differently where needed.
    """
    default_limit = 20
    max_limit = 100
    offset_query_param = 'skip'

    def get_paginated_response(self, data):
        return Response({
            'total': self.count,
            'datasets': data,
        })
