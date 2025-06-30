import requests
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.permissions import IsStaffAuthOrReadOnly

from books.models import BookModel
from books.serializers import BookSerializer

from books.services.google_books_api import search_google_api, import_from_google_api


class BookViewSetAPI(viewsets.ModelViewSet):
    queryset = BookModel.objects.prefetch_related("author", "categories")
    serializer_class = BookSerializer
    
    permission_classes  = [IsStaffAuthOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    search_fields = ["title", "isbn_13", "isbn_10", "authors__name", "categories__name"]
    ordering_fields = ['price', 'created_at', 'page_count']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'], url_path='search-google')
    def search_google_books(self, request):
        query_params_ = self.request.query_params.get('q')
        if not query_params_:
            return Response({
                "Detail": "Parâmetro 'q' é obrigatório."
            }, status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = search_google_api(query=query_params_)
            return Response(data)
        except requests.exceptions.RequestException:
            return Response({"detail": "Erro ao se comunicar com a API do Google."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['post'], url_path='import-google')
    def import_from_google_books(self, request):
        google_id = request.data.get('google_books_id')
        if not google_id:
            return Response({"detail": "Campo 'google_books_id' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = import_from_google_api(google_id)
            serializer = self.get_serializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            status_code = status.HTTP_409_CONFLICT if "cadastrado" in str(e) else status.HTTP_400_BAD_REQUEST
            return Response({"detail": str(e)}, status=status_code)
        except requests.exceptions.RequestException:
             return Response({"detail": "Erro de comunicação com a API do Google ao importar."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    