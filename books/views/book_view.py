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
    """
    BookViewSetAPI é uma ViewSet baseada em ModelViewSet para gerenciar operações relacionadas ao modelo BookModel.
    Funcionalidades principais:
    - Permite operações CRUD para livros, com permissões restritas a usuários staff para escrita e leitura aberta para outros.
    - Suporta filtros, busca e ordenação por campos como título, ISBN, autor, categoria, preço, data de criação e número de páginas.
    - Endpoint customizado GET /search-google: Busca livros na API do Google Books a partir do parâmetro de consulta 'q'.
    - Endpoint customizado POST /import-google: Importa um livro da Google Books API usando o 'google_books_id' informado no corpo da requisição.
    Atributos:
        queryset: Queryset base com prefetch de autores e categorias.
        serializer_class: Serializador utilizado para o modelo de livro.
        permission_classes: Permissões aplicadas à viewset.
        filter_backends: Backends de filtro, busca e ordenação.
        search_fields: Campos disponíveis para busca textual.
        ordering_fields: Campos disponíveis para ordenação.
        ordering: Ordenação padrão dos resultados.
    Métodos:
        search_google_books(request): Busca livros na Google Books API.
        import_from_google_books(request): Importa um livro da Google Books API para o banco local.
    """
    queryset = BookModel.objects.prefetch_related("authors", "categories")
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
    