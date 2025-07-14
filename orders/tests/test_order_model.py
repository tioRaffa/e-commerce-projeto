import pytest
from decimal import Decimal
from django.db import IntegrityError

# Importe os modelos necessários para os testes
from django.contrib.auth.models import User
from orders.models import OrderModel
from addresses.models import AddressModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db


# --- Fixtures para preparar dados de teste ---

@pytest.fixture
def user():
    """Cria um usuário de teste."""
    return User.objects.create_user(username='test_order_user', email='order@example.com')

@pytest.fixture
def address(user):
    """Cria um endereço de teste para o usuário."""
    # Supondo que a relação seja Address -> User
    return AddressModel.objects.create(user=user, zip_code='88000000', street='Rua Teste Pedido', number='123')


# --- Testes de Sucesso (Caminho Feliz) ---

def test_order_model_creation_success(user, address):
    """
    TESTE DE SUCESSO: Garante que um Order pode ser criado com dados válidos e com o status padrão correto.
    """
    order = OrderModel.objects.create(
        user=user,
        address=address,
        total_items_price=Decimal('150.75'),
        shipping_cost=Decimal('25.25')
    )
    
    assert OrderModel.objects.count() == 1
    assert order.user == user
    assert order.address == address
    # Verifica se o status padrão foi aplicado corretamente
    assert order.status == OrderModel.OrderStatus.PENDING_PAYMENT

def test_final_total_property_calculates_correctly(user, address):
    """
    TESTE DE SUCESSO: Garante que a property 'final_total' soma os valores corretamente.
    """
    order = OrderModel(
        user=user,
        address=address,
        total_items_price=Decimal('100.00'),
        shipping_cost=Decimal('19.99')
    )
    
    # 100.00 + 19.99 = 119.99
    assert order.final_total == Decimal('119.99')

def test_str_method(user):
    """
    TESTE DE SUCESSO: Garante que a representação em string do objeto é amigável.
    """
    order = OrderModel.objects.create(
        user=user,
        total_items_price=1,
        shipping_cost=1
    )
    
    expected_str = f"Pedido {order.id} - {user.username}"
    assert str(order) == expected_str


# --- Testes de Relacionamento e Comportamento ---

def test_on_delete_user_sets_user_to_null(user, address):
    """
    TESTE DE COMPORTAMENTO: Garante que, se um usuário for deletado, o campo 'user'
    no Order se torna NULO, mas o pedido em si não é deletado.
    """
    order = OrderModel.objects.create(user=user, address=address, total_items_price=1, shipping_cost=1)
    
    # Deleta o usuário
    user_id = user.id
    User.objects.filter(id=user_id).delete()
    
    # Recarrega o pedido do banco de dados
    order.refresh_from_db()
    
    assert OrderModel.objects.count() == 1
    assert order.user is None

def test_on_delete_address_sets_address_to_null(user, address):
    """
    TESTE DE COMPORTAMENTO: Garante que, se um endereço for deletado, o campo 'address'
    no Order se torna NULO, mas o pedido não é deletado.
    """
    order = OrderModel.objects.create(user=user, address=address, total_items_price=1, shipping_cost=1)
    
    # Deleta o endereço
    address_id = address.id
    AddressModel.objects.filter(id=address_id).delete()
    
    order.refresh_from_db()
    
    assert OrderModel.objects.count() == 1
    assert order.address is None


# --- Testes de Erro e Validação de Constraints ---

def test_stripe_payment_intent_id_is_unique(user):
    """
    TESTE DE ERRO: Garante que a constraint 'unique=True' no campo do Stripe ID funciona.
    """
    # Cria um primeiro pedido com um ID de pagamento
    OrderModel.objects.create(
        user=user, total_items_price=1, shipping_cost=1,
        stripe_payment_intent_id='pi_12345_abc'
    )
    
    # Tenta criar um SEGUNDO pedido com o MESMO ID de pagamento
    with pytest.raises(IntegrityError):
        OrderModel.objects.create(
            user=user, total_items_price=1, shipping_cost=1,
            stripe_payment_intent_id='pi_12345_abc'
        )

def test_multiple_orders_can_have_null_stripe_id(user):
    """
    TESTE DE SUCESSO (CASO DE BORDA): Garante que a constraint 'unique=True' permite
    múltiplos valores NULOS, essencial para pedidos pendentes.
    """
    # Cria dois pedidos, ambos sem um ID de pagamento (o valor padrão é NULL)
    OrderModel.objects.create(user=user, total_items_price=1, shipping_cost=1)
    OrderModel.objects.create(user=user, total_items_price=1, shipping_cost=1)
    
    # O teste passa se nenhum IntegrityError for levantado.
    assert OrderModel.objects.count() == 2