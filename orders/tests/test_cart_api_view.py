import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import BookModel

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db


# --- Fixtures para preparar dados de teste ---

@pytest.fixture
def api_client():
    """Cria uma instância do cliente de API para os testes."""
    return APIClient()

@pytest.fixture
def book_with_stock():
    """Cria um livro de teste ativo e com estoque."""
    return BookModel.objects.create(title="Livro com Estoque", price="50.00", stock=10, is_active=True)

@pytest.fixture
def book_without_stock():
    """Cria um livro de teste ativo, mas sem estoque."""
    return BookModel.objects.create(title="Livro sem Estoque", price="40.00", stock=0, is_active=True)


# --- Testes para a CartAPIView ---

class TestCartAPI:
    def test_get_empty_cart(self, api_client):
        """
        TESTE DE SUCESSO: Garante que, para uma nova sessão, o carrinho retornado está vazio e com a estrutura correta.
        """
        url = reverse('cart-api')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # A estrutura base deve ser retornada mesmo para um carrinho vazio
        assert response.data == {'items': {}}

    def test_add_item_to_cart_success(self, api_client, book_with_stock):
        """
        TESTE DE SUCESSO: Garante que um item pode ser adicionado ao carrinho com sucesso.
        """
        url = reverse('cart-api')
        payload = {'book_id': book_with_stock.id, 'quantity': 2}
        response = api_client.post(url, data=payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert str(book_with_stock.id) in response.data['items']
        assert response.data['items'][str(book_with_stock.id)]['quantity'] == 2

    def test_add_item_insufficient_stock(self, api_client, book_with_stock):
        """
        TESTE DE FALHA: Garante que a API retorna um erro se a quantidade for maior que o estoque.
        """
        url = reverse('cart-api')
        # Tenta comprar 11 unidades de um livro com estoque 10
        payload = {'book_id': book_with_stock.id, 'quantity': 11}
        response = api_client.post(url, data=payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Estoque insuficiente' in response.data['detail']

    def test_delete_item_from_cart(self, api_client, book_with_stock):
        """
        TESTE DE SUCESSO: Garante que um item pode ser removido do carrinho.
        """
        url = reverse('cart-api')
        # Primeiro, adiciona o item
        api_client.post(url, data={'book_id': book_with_stock.id, 'quantity': 1}, format='json')

        # Agora, remove o item
        delete_payload = {'book_id': book_with_stock.id}
        response = api_client.delete(url, data=delete_payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert str(book_with_stock.id) not in response.data.get('items', {})

    def test_cart_expiration(self, api_client, book_with_stock):
        """
        TESTE DE LÓGICA: Garante que o carrinho é limpo se estiver expirado.
        """
        url = reverse('cart-api')
        # Adiciona um item para criar o carrinho e a data de expiração
        api_client.post(url, data={'book_id': book_with_stock.id, 'quantity': 1}, format='json')

        # Usamos 'patch' para simular a passagem do tempo, avançando o relógio em 61 minutos
        future_time = datetime.now(timezone.utc) + timedelta(minutes=61)
        with patch('django.utils.timezone.now', return_value=future_time):
            # Fazemos uma nova requisição GET. A lógica de expiração deve ser acionada.
            response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # O carrinho retornado deve estar vazio
        assert response.data == {'items': {}}


# --- Testes para a CartShippingSelectionAPIView ---

class TestCartShippingSelectionAPI:
    def test_select_shipping_option_success(self, api_client, book_with_stock):
        """
        TESTE DE SUCESSO: Garante que uma opção de frete pode ser adicionada ao carrinho.
        """
        cart_url = reverse('cart-api')
        shipping_url = reverse('cart-select-shipping')
        
        # Primeiro, adiciona um item ao carrinho para que ele exista
        api_client.post(cart_url, data={'book_id': book_with_stock.id, 'quantity': 1}, format='json')

        # Agora, seleciona uma opção de frete
        shipping_payload = {
            "shipping_option": {
                "name": "SEDEX",
                "price": "25.50"
            }
        }
        response = api_client.post(shipping_url, data=shipping_payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'shipping_option' in response.data
        assert response.data['shipping_option']['name'] == 'SEDEX'

    def test_select_shipping_option_invalid_payload(self, api_client):
        """
        TESTE DE FALHA: Garante que a API retorna um erro se o payload do frete for inválido.
        """
        shipping_url = reverse('cart-select-shipping')
        # Envia um objeto sem as chaves 'name' e 'price'
        invalid_payload = {"shipping_option": {"id": 1}}
        response = api_client.post(shipping_url, data=invalid_payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'obrigatória' in response.data['detail']
