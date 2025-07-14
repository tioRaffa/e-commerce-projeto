import pytest
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Importe os modelos necessários para os testes
from django.contrib.auth.models import User
from orders.models import OrderModel, OrderItemModel
from books.models import BookModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db


# --- Fixtures para preparar dados de teste ---

@pytest.fixture
def user():
    """Cria um usuário de teste."""
    return User.objects.create_user(username='test_model_user')

@pytest.fixture
def order(user):
    """Cria um pedido de teste ao qual os itens serão associados."""
    return OrderModel.objects.create(
        user=user,
        total_items_price=Decimal('0.00'),
        shipping_cost=Decimal('0.00')
    )

@pytest.fixture
def book():
    """Cria um livro de teste."""
    return BookModel.objects.create(
        title="O Guia do Mochileiro das Galáxias",
        price=Decimal('42.00'),
        stock=100
    )


# --- Testes de Sucesso (Caminho Feliz) ---

def test_order_item_creation_success(order, book):
    """
    TESTE DE SUCESSO: Garante que um OrderItem pode ser criado com dados válidos.
    """
    order_item = OrderItemModel.objects.create(
        order=order,
        book=book,
        book_title_snapshot=book.title,
        quantity=2,
        price_at_purchase=book.price
    )
    
    assert OrderItemModel.objects.count() == 1
    assert order_item.order == order
    assert order_item.book == book
    assert order_item.quantity == 2
    assert order_item.price_at_purchase == Decimal('42.00')
    assert order_item.book_title_snapshot == "O Guia do Mochileiro das Galáxias"

def test_total_price_property(order, book):
    """
    TESTE DE SUCESSO: Garante que a property 'total_price' calcula o valor corretamente.
    """
    order_item = OrderItemModel(
        order=order,
        book=book,
        quantity=3,
        price_at_purchase=Decimal('10.50')
    )
    
    # 3 * 10.50 = 31.50
    assert order_item.total_price == Decimal('31.50')

def test_str_method(order, book):
    """
    TESTE DE SUCESSO: Garante que a representação em string do objeto é amigável.
    """
    order_item = OrderItemModel.objects.create(
        order=order,
        book=book,
        book_title_snapshot=book.title,
        quantity=5,
        price_at_purchase=book.price
    )
    
    expected_str = f'5x {book.title} No Pedido #{order.pk}'
    assert str(order_item) == expected_str


# --- Testes de Relacionamento e Comportamento ---

def test_on_delete_book_sets_book_to_null(order, book):
    """
    TESTE DE COMPORTAMENTO: Garante que, se um livro for deletado, o campo 'book'
    no OrderItem se torna NULO, mas o OrderItem em si não é deletado.
    """
    order_item = OrderItemModel.objects.create(
        order=order,
        book=book,
        quantity=1,
        price_at_purchase=book.price,
        book_title_snapshot=book.title
    )
    
    # Deleta o livro
    book_id = book.id
    BookModel.objects.filter(id=book_id).delete()
    
    # Recarrega o order_item do banco de dados para ver o estado atualizado
    order_item.refresh_from_db()
    
    # O OrderItem ainda deve existir
    assert OrderItemModel.objects.count() == 1
    # O campo 'book' deve ser NULO
    assert order_item.book is None
    # Mas o 'book_title_snapshot' deve ter preservado o nome original
    assert order_item.book_title_snapshot == "O Guia do Mochileiro das Galáxias"


# --- Testes de Erro e Validação de Constraints ---

def test_quantity_cannot_be_negative(order, book):
    """
    TESTE DE ERRO: Garante que a constraint do banco impede valores negativos.
    """
    with pytest.raises(IntegrityError):
        OrderItemModel.objects.create(
            order=order,
            book=book,
            book_title_snapshot="test",
            price_at_purchase=10,
            quantity=-1
        )

def test_quantity_can_be_zero_by_default(order, book):
    """
    TESTE DE COMPORTAMENTO: Confirma que o PositiveIntegerField padrão permite zero.
    """
    # Este teste deve passar sem erros, pois PositiveIntegerField permite 0.
    OrderItemModel.objects.create(
        order=order,
        book=book,
        book_title_snapshot="test",
        price_at_purchase=10,
        quantity=0
    )
    assert OrderItemModel.objects.filter(quantity=0).exists()

# --- Sugestão de Melhoria e Teste Adicional ---
# Para impedir que a quantidade seja 0, você pode adicionar um validador ao seu modelo:
#
# Em apps/orders/models.py:
# from django.core.validators import MinValueValidator
#
# class OrderItemModel(models.Model):
#     ...
#     quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
#
# Depois de adicionar o validador e rodar as migrações, o teste abaixo passaria.

def test_quantity_cannot_be_zero_with_validator(order, book):
    """
    TESTE DE VALIDAÇÃO: Garante que, se um MinValueValidator(1) for adicionado ao modelo,
    a criação com quantidade 0 levanta um ValidationError.
    """
    # Adiciona o validador ao campo do modelo para este teste
    quantity_field = OrderItemModel._meta.get_field('quantity')
    quantity_field.validators.append(MinValueValidator(1))

    with pytest.raises(ValidationError):
        item = OrderItemModel(
            order=order,
            book=book,
            book_title_snapshot="test",
            price_at_purchase=10,
            quantity=0
        )
        item.full_clean() # A validação do modelo é chamada aqui

    # Remove o validador para não afetar outros testes
    quantity_field.validators.pop()