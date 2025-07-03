import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from books.models import BookModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db

# Testes de Ações Customizadas
@patch('books.views.book_view.search_google_api')
def test_search_google_books(mock_search, api_client):
    """
    Testa a busca de livros na API do Google.
    """
    mock_search.return_value = {'items': [{'volumeInfo': {'title': 'Google Book'}}]}
    url = reverse('book-api-search-google-books')
    response = api_client.get(url, {'q': 'testing'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['items'][0]['volumeInfo']['title'] == 'Google Book'
    mock_search.assert_called_once_with(query='testing')

@patch('books.views.book_view.import_from_google_api')
def test_import_from_google_books(mock_import, api_client, create_staff_user, author, category):
    """
    Testa a importação de um livro da API do Google.
    """
    api_client.force_authenticate(user=create_staff_user)
    
    # Mock do livro que seria retornado pela função de importação
    mock_book = BookModel(
        title='Imported Book',
        google_books_id='12345',
        publisher='Google Publisher',
        price=50.00,
        stock=2,
        is_active=True,
        weight_g=400,
        height_cm=22,
        width_cm=16,
        length_cm=3
    )
    mock_book.save()
    mock_book.authors.add(author)
    mock_book.categories.add(category)
    
    mock_import.return_value = mock_book
    
    url = reverse('book-api-import-from-google-books')
    data = {'google_books_id': '12345'}
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'Imported Book'
    mock_import.assert_called_once_with('12345')
