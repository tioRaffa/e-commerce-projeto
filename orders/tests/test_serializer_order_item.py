import pytest
from decimal import Decimal

# Importe os modelos e serializers que você vai testar
from orders.models import OrderModel, OrderItemModel
from books.models import BookModel, AuthorModel
from django.contrib.auth.models import User
from orders.serializer.order_item_serializer import OrderItemReadSerializer, OrderItemCreateSerializer

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db


# --- Fixtures para preparar dados de teste ---

@pytest.fixture
def book():
    """Cria um livro de teste ativo e com estoque."""
    author = AuthorModel.objects.create(name="Autor de Teste")
    book = BookModel.objects.create(
        title="Livro para Serializer",
        price=Decimal('29.99'),
        stock=10,
        is_active=True
    )
    book.authors.add(author)
    return book

@pytest.fixture
def inactive_book():
    """Cria um livro de teste inativo."""
    return BookModel.objects.create(title="Livro Inativo",         price=Decimal('19.99'), stock=5, is_active=False)

@pytest.fixture
def order_item(book):
    """Cria um OrderItem de teste para ser usado no serializer de leitura."""
    user = User.objects.create_user(username="testserializeruser")
    order = OrderModel.objects.create(
        user=user,
        total_items_price=100,
        shipping_cost=20,
        status=OrderModel.OrderStatus.PROCESSING
    )
    return OrderItemModel.objects.create(
        order=order,
        book=book,
        book_title_snapshot=book.title,
        quantity=2,
        price_at_purchase=Decimal('29.99')
    )


# --- Testes para o OrderItemReadSerializer ---

def test_order_item_read_serializer_contains_expected_fields(order_item):
    """
    TESTE DE SUCESSO: Garante que o serializer de leitura retorna os campos corretos.
    """
    serializer = OrderItemReadSerializer(instance=order_item)
    data = serializer.data
    
    # Verifica se as chaves principais existem
    assert 'book' in data
    assert 'quantity' in data
    assert 'price_at_purchase' in data
    assert 'total_price' in data
    
    # Verifica os valores
    assert data['quantity'] == 2
    assert data['price_at_purchase'] == '29.99'
    assert data['total_price'] == Decimal('59.98') # 2 * 29.99
    
    # Verifica se os dados do livro aninhado estão corretos
    assert data['book']['title'] == 'Livro para Serializer'


# --- Testes para o OrderItemCreateSerializer ---

def test_order_item_create_serializer_valid_data(book):
    """
    TESTE DE SUCESSO: Garante que o serializer de escrita é válido com dados corretos.
    """
    data = {'book_id': book.id, 'quantity': 1}
    serializer = OrderItemCreateSerializer(data=data)
    
    assert serializer.is_valid() is True

def test_order_item_create_serializer_invalid_book_id():
    """
    TESTE DE FALHA: Garante que o serializer falha se o book_id não existir.
    """
    data = {'book_id': 999, 'quantity': 1} # ID de livro que não existe
    serializer = OrderItemCreateSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'Livro não encotrado ou Inativo' in str(serializer.errors['book_id'])

def test_order_item_create_serializer_inactive_book(inactive_book):
    """
    TESTE DE FALHA: Garante que o serializer falha se o livro estiver inativo.
    """
    data = {'book_id': inactive_book.id, 'quantity': 1}
    serializer = OrderItemCreateSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'Livro não encotrado ou Inativo' in str(serializer.errors['book_id'])

def test_order_item_create_serializer_invalid_quantity(book):
    """
    TESTE DE FALHA: Garante que o serializer falha se a quantidade for zero ou negativa.
    """
    data = {'book_id': book.id, 'quantity': 0}
    serializer = OrderItemCreateSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'quantity' in serializer.errors

def test_order_item_create_serializer_missing_data():
    """
    TESTE DE FALHA: Garante que o serializer falha se faltarem campos obrigatórios.
    """
    data = {'quantity': 1} # Faltando book_id
    serializer = OrderItemCreateSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'book_id' in serializer.errors
    assert 'Este campo é obrigatório.' in str(serializer.errors['book_id'])