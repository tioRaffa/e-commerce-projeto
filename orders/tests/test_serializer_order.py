import pytest
from decimal import Decimal

from django.contrib.auth.models import User
from orders.models import OrderModel, OrderItemModel
from books.models import BookModel
from addresses.models import AddressModel
from orders.serializer import OrderReadSerializer, OrderCreateSerializer

from rest_framework.request import Request
from django.http import HttpRequest

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_a():
    return User.objects.create_user(username='usera', email='usera@example.com')

@pytest.fixture
def user_b():
    return User.objects.create_user(username='userb', email='userb@example.com')

@pytest.fixture
def address_for_user_a(user_a):
    return AddressModel.objects.create(user=user_a, zip_code='11111111', street='Rua A', number='1')

@pytest.fixture
def address_for_user_b(user_b):
    return AddressModel.objects.create(user=user_b, zip_code='22222222', street='Rua B', number='2')

@pytest.fixture
def book():
    return BookModel.objects.create(title="Livro de Teste para Pedido", price=Decimal("99.99"), stock=10)

@pytest.fixture
def complete_order(user_a, address_for_user_a, book):
    order = OrderModel.objects.create(
        user=user_a,
        address=address_for_user_a,
        status=OrderModel.OrderStatus.PROCESSING,
        total_items_price=Decimal("99.99"),
        shipping_cost=Decimal("15.00"),
        shipping_method="SEDEX",
        tracking_code="BR123456789",
    )
    OrderItemModel.objects.create(
        order=order,
        book=book,
        quantity=1,
        price_at_purchase=Decimal("99.99"),
        book_title_snapshot=book.title
    )
    return order


# --- Testes para o OrderReadSerializer ---

def test_order_read_serializer_contains_expected_fields(complete_order):
    serializer = OrderReadSerializer(instance=complete_order)
    data = serializer.data

    assert 'id' in data
    assert 'user' in data
    assert 'status' in data
    assert 'final_total' in data
    assert 'address' in data
    assert 'items' in data
    
    assert data['final_total'] == Decimal('114.99')
    assert data['user'] == 'usera'
    assert data['address']['street'] == 'Rua A'
    assert len(data['items']) == 1


# --- Testes para o OrderCreateSerializer ---

@pytest.fixture
def mock_request(user_a):
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = user_a
    return request

def test_order_create_serializer_valid_data(address_for_user_a, mock_request):
    data = {
        "address_id": address_for_user_a.id,
        "shipping_method": "SEDEX",
        "payment_method_id": "pm_card_visa"
    }
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})
    
    assert serializer.is_valid(raise_exception=True) is True
    assert serializer.validated_data['address_id'] == address_for_user_a

def test_order_create_serializer_valid_data_no_shipping_method(address_for_user_a, mock_request):
    data = {
        "address_id": address_for_user_a.id,
        "payment_method_id": "pm_card_visa"
    }
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})
    
    assert serializer.is_valid(raise_exception=True) is True
    assert serializer.validated_data['address_id'] == address_for_user_a
    assert 'shipping_method' not in serializer.validated_data

def test_order_create_serializer_invalid_address(mock_request):
    data = {"address_id": 999, "shipping_method": "SEDEX", "payment_method_id": "pm_123"}
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})
    
    assert serializer.is_valid() is False
    assert 'address_id' in serializer.errors
    assert "Endereço inválido ou não pertence a este usuário." in str(serializer.errors['address_id'])

def test_order_create_serializer_address_not_owned_by_user(address_for_user_b, mock_request):
    data = {"address_id": address_for_user_b.id, "shipping_method": "SEDEX", "payment_method_id": "pm_123"}
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})
    
    assert serializer.is_valid() is False
    assert 'address_id' in serializer.errors
    assert "Endereço inválido ou não pertence a este usuário." in str(serializer.errors['address_id'])

def test_order_create_serializer_missing_required_field(address_for_user_a, mock_request):
    data = {"address_id": address_for_user_a.id, "shipping_method": "SEDEX"}
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})
    
    assert serializer.is_valid() is False
    assert 'payment_method_id' in serializer.errors
    assert 'Este campo é obrigatório.' in str(serializer.errors['payment_method_id'])

def test_order_create_serializer_empty_data(mock_request):
    data = {}
    serializer = OrderCreateSerializer(data=data, context={'request': mock_request})

    assert serializer.is_valid() is False
    assert 'address_id' in serializer.errors
    assert 'payment_method_id' in serializer.errors
    assert 'Este campo é obrigatório.' in str(serializer.errors['address_id'])
    assert 'Este campo é obrigatório.' in str(serializer.errors['payment_method_id'])