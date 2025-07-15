
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from orders.models import OrderModel, OrderItemModel
from addresses.models import AddressModel
from books.models import BookModel

pytestmark = pytest.mark.django_db

# --- Fixtures ---

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='password123')

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='otheruser', password='password123')

@pytest.fixture
def book(db):
    return BookModel.objects.create(title="Test Book", price=50.00, stock=10)

@pytest.fixture
def address(db, user):
    return AddressModel.objects.create(user=user, street="123 Test St", city="Testville", zip_code="12345")

@pytest.fixture
def order(db, user, address):
    return OrderModel.objects.create(user=user, address=address, total_items_price=50.00, shipping_cost=15.00)

@pytest.fixture
def order_item(db, order, book):
    return OrderItemModel.objects.create(order=order, book=book, quantity=1, price_per_unit=50.00)

@pytest.fixture
def cart_with_item(api_client, book):
    session = api_client.session
    session['cart'] = {
        'items': {str(book.id): {'quantity': 1, 'price': str(book.price)}},
        'shipping_option': {'name': 'SEDEX', 'price': str(15.00)}
    }
    session.save()
    return api_client

# --- Testes para OrderViewSet ---

class TestOrderViewSet:

    # --- Testes de Listagem e Recuperação ---

    def test_list_orders_authenticated(self, api_client, user, order):
        api_client.force_authenticate(user=user)
        url = reverse('order-api-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == order.id

    def test_list_orders_unauthenticated(self, api_client):
        url = reverse('order-api-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_own_order(self, api_client, user, order):
        api_client.force_authenticate(user=user)
        url = reverse('order-api-detail', kwargs={'pk': order.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id

    def test_cannot_retrieve_other_user_order(self, api_client, user, other_user, address):
        other_order = OrderModel.objects.create(user=other_user, address=address, total_items_price=100.00, shipping_cost=15.00)
        api_client.force_authenticate(user=user)
        url = reverse('order-api-detail', kwargs={'pk': other_order.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --- Testes de Criação de Pedido ---

    @patch('orders.views.order_viewset.create_order_from_cart')
    def test_create_order_success(self, mock_create_order, user, address, book):
        """
        Testa se a ViewSet de Pedidos consegue iniciar o processo de criação com sucesso.
        """
        # 1. PREPARAÇÃO: Criamos um cliente e autenticamos.
        #    Vamos usar este mesmo cliente para toda a jornada.
        client = APIClient()
        client.force_authenticate(user=user)

        # 2. AÇÃO PRELIMINAR: Simulamos o usuário adicionando um item ao carrinho.
        #    Isso garante que a sessão do 'client' não estará mais vazia.
        cart_url = reverse('cart-api') # Usa o nome da rota do carrinho que você já configurou
        response_cart = client.post(cart_url, data={'book_id': book.id, 'quantity': 1}, format='json')
        assert response_cart.status_code == status.HTTP_200_OK # Garante que o item foi adicionado

        # 3. CONFIGURAÇÃO DO MOCK: Dizemos o que a função de serviço deve retornar
        #    quando for chamada pela view.
        mock_order = MagicMock(spec=OrderModel)
        mock_order.id = 1
        mock_order.status = OrderModel.OrderStatus.PROCESSING
        mock_create_order.return_value = mock_order
        
        # 4. AÇÃO PRINCIPAL: Agora sim, tentamos criar o pedido.
        order_url = reverse('order-api-list') # Nome padrão do router para a ação de criar
        payload = {'address_id': address.id, 'payment_method_id': 'pm_card_visa', 'shipping_method': 'SEDEX'}
        response = client.post(order_url, data=payload, format='json')
        
        # 5. VERIFICAÇÃO FINAL
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica se a função de serviço mockada foi chamada corretamente pela view
        mock_create_order.assert_called_once()
        
        # Verifica se o carrinho foi limpo da sessão após a criação do pedido
        session = client.session
        assert 'cart' not in session or not session.get('cart')

    def test_create_order_empty_cart(self, api_client, user, address):
        api_client.force_authenticate(user=user)
        url = reverse('order-api-list')
        payload = {'address_id': address.id, 'payment_method_id': 'pm_card_visa'}
        response = api_client.post(url, data=payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Seu carrinho esta vazio' in response.data['detail']

    @patch('orders.views.order_viewset.create_order_from_cart', side_effect=ValueError("Erro de processamento"))
    def test_create_order_service_exception(self, mock_create_order, api_client, user, address, cart_with_item):
        api_client.force_authenticate(user=user)
        url = reverse('order-api-list')
        payload = {'address_id': address.id, 'payment_method_id': 'pm_card_visa'}
        response = api_client.post(url, data=payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Erro de processamento' in response.data['detail']

    # --- Testes de Cancelamento de Pedido ---

    @patch('orders.views.order_viewset.cancel_order_service')
    def test_cancel_order_success(self, mock_cancel_service, api_client, user, order):
        api_client.force_authenticate(user=user)
        order.status = OrderModel.OrderStatus.PROCESSING
        order.save()

        url = reverse('order-api-cancel-order', kwargs={'pk': order.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        mock_cancel_service.assert_called_once_with(order)

    def test_cancel_order_wrong_status(self, api_client, user, order):
        api_client.force_authenticate(user=user)
        order.status = OrderModel.OrderStatus.DELIVERED
        order.save()

        url = reverse('order-api-cancel-order', kwargs={'pk': order.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Não é possivel cancelar um pedido com o status 'Entregue'" in response.data['detail']

    def test_cannot_cancel_other_user_order(self, api_client, user, other_user, address):
        other_order = OrderModel.objects.create(user=other_user, address=address, status=OrderModel.OrderStatus.PROCESSING, total_items_price=100.00, shipping_cost=15.00)
        api_client.force_authenticate(user=user)
        url = reverse('order-api-cancel-order', kwargs={'pk': other_order.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
