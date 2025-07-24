
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
import requests
import re

from orders.services.melhor_envio import generate_shipping_label_service
from orders.models import OrderModel, OrderItemModel
from django.contrib.auth.models import User
from addresses.models import AddressModel
from books.models.book_model import BookModel

@pytest.mark.django_db
def test_generate_shipping_label_happy_path(mocker):
    """
    Testa o caminho feliz da geração de etiqueta de envio.
    """
    # Mocks
    mock_requests_post = mocker.patch('requests.post')
    mock_requests_get = mocker.patch('requests.get')
    mocker.patch('time.sleep', return_value=None)  # Evita a espera real

    # Configuração das respostas mockadas da API
    mock_cart_response = MagicMock()
    mock_cart_response.status_code = 200
    mock_cart_response.json.return_value = {'id': 'test-order-id'}

    mock_checkout_response = MagicMock()
    mock_checkout_response.status_code = 200

    mock_generate_response = MagicMock()
    mock_generate_response.status_code = 200

    mock_order_details_response = MagicMock()
    mock_order_details_response.status_code = 200
    mock_order_details_response.json.return_value = {'tracking': 'TEST-TRACKING-123'}

    # Define a sequência de respostas para as chamadas POST e GET
    mock_requests_post.side_effect = [
        mock_cart_response, 
        mock_checkout_response, 
        mock_generate_response
    ]
    mock_requests_get.return_value = mock_order_details_response

    # Dados de teste
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    user.profile.cpf = '123.456.789-00'
    user.profile.phone_number = '+5511999999999'
    user.profile.save()
    address = AddressModel.objects.create(user=user, zip_code='12345-678', street='Test Street', number='123', city='Test City', state='TS')
    book = BookModel.objects.create(title='Test Book', price=Decimal('29.90'), weight_g=Decimal('200'))
    
    order = OrderModel.objects.create(
        user=user, 
        address=address, 
        total_items_price=Decimal('29.90'),
        shipping_cost=Decimal('5.00'), # Adicionado custo de frete para o teste
        shipping_service_id=1 # ID do serviço de frete (ex: PAC)
    )
    OrderItemModel.objects.create(order=order, book=book, quantity=1, price_at_purchase=book.price)

    # Execução
    updated_order = generate_shipping_label_service(order)

    # Asserções
    assert updated_order.status == OrderModel.OrderStatus.SHIPPED
    assert updated_order.melhor_envio_order_id == 'test-order-id'
    assert updated_order.tracking_code == 'TEST-TRACKING-123'
    
    # Verifica se o order.save() foi chamado corretamente
    order.refresh_from_db()
    assert order.status == OrderModel.OrderStatus.SHIPPED
    assert order.tracking_code == 'TEST-TRACKING-123'


@pytest.mark.django_db
def test_generate_shipping_label_missing_service_id():
    """
    Testa se um ValueError é levantado se o ID do serviço de frete não for fornecido.
    """
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    user.profile.cpf = '123.456.789-00'
    user.profile.phone_number = '+5511999999999'
    user.profile.save()
    order = OrderModel.objects.create(
    user=user, 
    total_items_price=Decimal('50.00'), 
    shipping_cost=Decimal('0.00'),
    shipping_service_id=None
    )

    with pytest.raises(ValueError, match='O pedido deve conter um servico de frete selecionado'):
        generate_shipping_label_service(order)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status_code, error_json, expected_message",
    [
        (401, {'error': 'Unauthorized'}, "Erro de validação do Melhor Envio: "),
        (422, {'errors': {'field': ['invalid']}}, re.escape("Erro de validação do Melhor Envio: {'field': ['invalid']}")),
        (500, {'error': 'Internal Server Error'}, "Erro de validação do Melhor Envio: ")
    ]
)
def test_generate_shipping_label_api_error(mocker, status_code, error_json, expected_message):
    """
    Testa o tratamento de diferentes erros HTTP da API.
    """
    mock_requests_post = mocker.patch('requests.post')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = error_json
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_post.return_value = mock_response

    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    user.profile.cpf = '123.456.789-00'
    user.profile.phone_number = '+5511999999999'
    user.profile.save()
    address = AddressModel.objects.create(user=user, zip_code='12345-678', city='Test City', state='TS')
    order = OrderModel.objects.create(user=user, address=address, total_items_price=Decimal('10.00'), shipping_cost=Decimal('2.00'), shipping_service_id=1)

    with pytest.raises(Exception, match=expected_message):
        generate_shipping_label_service(order)


@pytest.mark.django_db
def test_generate_shipping_label_no_tracking_code(mocker):
    """
    Testa o caso onde a API não retorna o código de rastreamento após a espera.
    """
    # Mocks (semelhante ao happy path, mas sem 'tracking' na resposta final)
    mock_requests_post = mocker.patch('requests.post')
    mock_requests_get = mocker.patch('requests.get')
    mocker.patch('time.sleep', return_value=None)

    mock_cart_response = MagicMock()
    mock_cart_response.json.return_value = {'id': 'test-order-id'}
    mock_requests_post.side_effect = [mock_cart_response, MagicMock(), MagicMock()]

    mock_order_details_response = MagicMock()
    mock_order_details_response.json.return_value = {'status': 'released'} # Sem a chave 'tracking'
    mock_requests_get.return_value = mock_order_details_response

    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    user.profile.cpf = '123.456.789-00'
    user.profile.phone_number = '+5511999999999'
    user.profile.save()
    address = AddressModel.objects.create(user=user, zip_code='12345-678', city='Test City', state='TS')
    order = OrderModel.objects.create(user=user, address=address, total_items_price=Decimal('10.00'), shipping_cost=Decimal('2.00'), shipping_service_id=1)

    with pytest.raises(Exception, match='Código de rastreamento não encontrado na resposta da API após aguardar.'):
        generate_shipping_label_service(order)

