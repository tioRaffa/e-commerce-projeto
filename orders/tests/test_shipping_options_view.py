
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from addresses.models import AddressModel
from books.models import BookModel

# Marcador para todos os testes no arquivo usarem o banco de dados
pytestmark = pytest.mark.django_db

# --- Fixtures ---

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='password123')

@pytest.fixture
def other_user():
    return User.objects.create_user(username='otheruser', password='password123')

@pytest.fixture
def user_address(user):
    return AddressModel.objects.create(
        user=user,
        street='Rua Teste',
        number='123',
        city='Cidade Teste',
        state='TS',
        zip_code='12345678',
        is_primary=True
    )

@pytest.fixture
def other_user_address(other_user):
    return AddressModel.objects.create(
        user=other_user,
        street='Rua Outro',
        number='456',
        city='Outra Cidade',
        state='OT',
        zip_code='87654321',
        is_primary=True
    )

@pytest.fixture
def book():
    return BookModel.objects.create(title='Livro para Frete', price=100.00, stock=5)

@pytest.fixture
def cart_with_item(api_client, book):
    session = api_client.session
    session['cart'] = {
        'items': {
            str(book.id): {'quantity': 1, 'price': str(book.price)}
        }
    }
    session.save()
    return session

# --- Testes para a View ShippingOptions ---

class TestShippingOptionsView:

    def test_shipping_options_unauthenticated(self, api_client, user_address):
        """
        TESTE DE SEGURANÇA: Garante que usuários não autenticados recebem erro 401.
        """
        url = reverse('shipping-options')
        response = api_client.post(url, data={'address_id': user_address.id}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_shipping_options_success(self, api_client, user, user_address, cart_with_item):
        """
        TESTE DE SUCESSO: Garante que as opções de frete são retornadas com sucesso.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        mock_shipping_data = [{'id': 1, 'name': 'SEDEX', 'price': '25.50'}]

        with patch('orders.views.shipping_options.calculate_shipping_with_melhor_envio', return_value=mock_shipping_data) as mock_calculate:
            response = api_client.post(url, data={'address_id': user_address.id}, format='json')

            assert response.status_code == status.HTTP_200_OK
            assert response.data == mock_shipping_data
            mock_calculate.assert_called_once_with(
                cart=cart_with_item['cart']['items'],
                zip_code=user_address.zip_code
            )

    def test_shipping_options_no_address_id(self, api_client, user, cart_with_item):
        """
        TESTE DE FALHA: Garante que um erro é retornado se 'address_id' não for fornecido.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        response = api_client.post(url, data={}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'O Id de endereço é obrigatorio' in response.data['detail']

    def test_shipping_options_empty_cart(self, api_client, user, user_address):
        """
        TESTE DE FALHA: Garante que um erro é retornado se o carrinho estiver vazio.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        response = api_client.post(url, data={'address_id': user_address.id}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'O carrinho esta vazio' in response.data['detail']

    def test_shipping_options_address_not_found(self, api_client, user, cart_with_item):
        """
        TESTE DE FALHA: Garante que um erro 404 é retornado para um ID de endereço inexistente.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        response = api_client.post(url, data={'address_id': 999}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_security_user_cannot_use_other_user_address(self, api_client, user, other_user_address, cart_with_item):
        """
        TESTE DE SEGURANÇA: Garante que um usuário não pode usar o endereço de outro usuário.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        response = api_client.post(url, data={'address_id': other_user_address.id}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_shipping_service_exception(self, api_client, user, user_address, cart_with_item):
        """
        TESTE DE FALHA: Garante que a view trata exceções do serviço de cálculo de frete.
        """
        api_client.force_authenticate(user=user)
        url = reverse('shipping-options')
        error_message = 'Erro na API de frete'
        with patch('orders.views.shipping_options.calculate_shipping_with_melhor_envio', side_effect=Exception(error_message)) as mock_calculate:
            response = api_client.post(url, data={'address_id': user_address.id}, format='json')
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert error_message in response.data['detail-erro']
            mock_calculate.assert_called_once()
