import pytest
from django.urls import reverse
from rest_framework import status
from books.models import BookModel, AuthorModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db

# Testes da API
def test_list_books_unauthenticated(api_client, book):
    """
    Testa se um usuário não autenticado pode listar os livros.
    """
    url = reverse('book-api-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1

def test_create_book_authenticated_staff(api_client, create_staff_user, author, category):
    """
    Testa se um usuário staff autenticado pode criar um livro.
    """
    api_client.force_authenticate(user=create_staff_user)
    url = reverse('book-api-list')
    data = {
        'title': 'New Book',
        'price': 30.00,
        'stock': 5,
        'is_active': True,
        'author_ids': [author.id],
        'category_ids': [category.id],
        'weight_g': 300,
        'height_cm': 20,
        'width_cm': 15,
        'length_cm': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert BookModel.objects.filter(title='New Book').exists()

def test_create_book_unauthenticated(api_client, author, category):
    """
    Testa se um usuário não autenticado não pode criar um livro.
    """
    url = reverse('book-api-list')
    data = {
        'title': 'Unauthorized Book',
        'price': 15.00,
        'author_ids': [author.id],
        'category_ids': [category.id]
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_book_authenticated_staff(api_client, create_staff_user, book):
    """
    Testa se um usuário staff pode atualizar um livro.
    """
    api_client.force_authenticate(user=create_staff_user)
    url = reverse('book-api-detail', kwargs={'pk': book.pk})
    data = {'price': 28.50}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    book.refresh_from_db()
    assert book.price == 28.50

def test_delete_book_authenticated_staff(api_client, create_staff_user, book):
    """
    Testa se um usuário staff pode deletar um livro.
    """
    api_client.force_authenticate(user=create_staff_user)
    url = reverse('book-api-detail', kwargs={'pk': book.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BookModel.objects.filter(pk=book.pk).exists()

def test_update_book_authors_authenticated_staff(api_client, create_staff_user, book):
    """
    Testa se um usuário staff pode atualizar os autores de um livro.
    """
    api_client.force_authenticate(user=create_staff_user)
    new_author = AuthorModel.objects.create(name='New Author')
    url = reverse('book-api-detail', kwargs={'pk': book.pk})
    data = {'author_ids': [new_author.id]}
    response = api_client.patch(url, data, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    book.refresh_from_db()
    assert book.authors.count() == 1
    assert book.authors.first() == new_author
