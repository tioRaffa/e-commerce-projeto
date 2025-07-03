import pytest
from rest_framework.test import APIClient
from books.models import BookModel, AuthorModel, CategoryModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    """
    Fixture para criar uma instância de APIClient para fazer requisições.
    """
    return APIClient()

@pytest.fixture
def create_user(django_user_model):
    """
    Fixture para criar um usuário comum.
    """
    return django_user_model.objects.create_user(
        username='testuser',
        password='password123',
        email='testuser@example.com'
    )

@pytest.fixture
def create_staff_user(django_user_model):
    """
    Fixture para criar um usuário com permissões de staff.
    """
    return django_user_model.objects.create_user(
        username='staffuser',
        password='password123',
        email='staffuser@example.com',
        is_staff=True
    )

@pytest.fixture
def author():
    """
    Fixture para criar um autor.
    """
    return AuthorModel.objects.create(name='Test Author')

@pytest.fixture
def category():
    """
    Fixture para criar uma categoria.
    """
    return CategoryModel.objects.create(name='Test Category')

@pytest.fixture
def book(author, category):
    """
    Fixture para criar um livro com dados completos para envio.
    """
    book = BookModel.objects.create(
        title='Test Book',
        publisher='Test Publisher',
        price=25.00,
        stock=10,
        is_active=True,
        weight_g=300,
        height_cm=20,
        width_cm=15,
        length_cm=2
    )
    book.authors.add(author)
    book.categories.add(category)
    return book
