from django.db import transaction
from django.conf import settings
import requests

from books.models import BookModel, AuthorModel, CategoryModel

def search_google_api(query: str) -> dict:
    """
    Pesquisa a API do Google Books por livros que correspondam à consulta fornecida.
    Args:
        query (str): O termo de busca para consultar a API do Google Books.
    Retorna:
        dict: A resposta JSON da API do Google Books como um dicionário Python.
    Exceções:
        requests.exceptions.RequestException: Se houver um problema com a requisição HTTP.
    Observação:
        Requer uma chave de API válida do Google Books definida em settings.GOOGLE_BOOKS_API_KEY.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    api_key = settings.GOOGLE_BOOKS_API_KEY
    
    params = {
        'q': query,
        'key': api_key,
        'maxResults': 20
    }

    try:
        response = requests.get(url=url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise

@transaction.atomic
def import_from_google_api(google_id: str) -> BookModel:
    """
    Importa um livro da API do Google Books e o cadastra no banco de dados.
    Parâmetros:
        google_id (str): O ID do livro na API do Google Books.
    Retorna:
        BookModel: Instância do livro criado.
    Lança:
        ValueError: Se o livro já estiver cadastrado, não for encontrado na API do Google,
                    ou se o volume retornado não possuir título.
        requests.exceptions.RequestException: Se ocorrer um erro na requisição à API do Google Books.
    Notas:
        - Cria ou recupera autores e categorias associados ao livro.
        - Utiliza transação atômica para garantir integridade dos dados.
    """
    if BookModel.objects.filter(google_books_id=google_id).exists():
        raise ValueError('Livro já cadastrado!')
    
    url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
    api_key = settings.GOOGLE_BOOKS_API_KEY

    try:
        response = requests.get(url=url, params={"key": api_key}, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise ValueError("Livro não encontrado na API do Google.")
        raise
    except requests.exceptions.RequestException:
        raise

    data = response.json()
    info = data.get('volumeInfo', {})

    if not info.get('title'):
        raise ValueError("Volume retornado pela API não possui Titulo!")
    
    authors = [AuthorModel.objects.get_or_create(name=name)[0] for name in info.get("authors", [])]
    categories = [CategoryModel.objects.get_or_create(name=name)[0] for name in info.get("categories", [])]

    isbn_13 = next((i['identifier'] for i in info.get('industryIdentifiers', []) if i['type'] == 'ISBN_13'), None)
    isbn_10 = next((i['identifier'] for i in info.get('industryIdentifiers', []) if i['type'] == 'ISBN_10'), None)

    book = BookModel.objects.create(
        google_books_id=google_id,
        title=info.get("title"),
        publisher=info.get('publisher'),
        published_date=info.get('publishedDate'),
        description=info.get('description'),
        page_count=info.get('pageCount') or 0,
        thumbnail_url=info.get("imageLinks", {}).get("thumbnail"),
        isbn_13=isbn_13,
        isbn_10=isbn_10,
        source='google_books'
    )
    book.authors.set(authors)
    book.categories.set(categories)

    return book