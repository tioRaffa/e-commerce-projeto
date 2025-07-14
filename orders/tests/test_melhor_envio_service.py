import pytest
from decimal import Decimal
import requests
from unittest.mock import MagicMock, patch

from orders.services.melhor_envio import (
    calculate_total_weight,
    calculate_shipping_with_melhor_envio,
    DEFAULT_PACKAGE_DIMENSIONS,
)
from books.models.book_model import BookModel


@pytest.fixture
def mock_book_model():
    with patch('books.models.book_model.BookModel.objects.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_config():
    with patch('orders.services.melhor_envio.config') as mock_cfg:
        mock_cfg.return_value = "mock_value"
        mock_cfg.side_effect = lambda key: {
            'ME_SANDBOX_URL': 'http://mock-melhor-envio.com',
            'ME_ACCESS_TOKEN': 'mock_token',
            'MY_STORE_ZIP_CODE': '12345-678',
        }.get(key, "mock_value")
        yield mock_cfg


@pytest.fixture
def mock_requests_post():
    with patch('requests.post') as mock_post:
        yield mock_post


# Tests for calculate_total_weight
def test_calculate_total_weight_empty_cart():
    cart_items = []
    assert calculate_total_weight(cart_items) == Decimal('0')


def test_calculate_total_weight_single_item_with_weight(mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    cart_items = [{'book_id': 1, 'quantity': 2}]
    assert calculate_total_weight(cart_items) == Decimal('1.0')


def test_calculate_total_weight_multiple_items_with_weight(mock_book_model):
    mock_book_model.side_effect = [
        MagicMock(weight_g=Decimal('250')),
        MagicMock(weight_g=Decimal('750')),
    ]
    cart_items = [{'book_id': 1, 'quantity': 2}, {'book_id': 2, 'quantity': 1}]
    # (250 * 2) + (750 * 1) = 500 + 750 = 1250g = 1.25kg
    assert calculate_total_weight(cart_items) == Decimal('1.25')


def test_calculate_total_weight_item_without_weight(mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=None)
    cart_items = [{'book_id': 1, 'quantity': 1}]
    assert calculate_total_weight(cart_items) == Decimal('0')


def test_calculate_total_weight_mixed_items(mock_book_model):
    mock_book_model.side_effect = [
        MagicMock(weight_g=Decimal('300')),
        MagicMock(weight_g=None),
        MagicMock(weight_g=Decimal('100')),
    ]
    cart_items = [
        {'book_id': 1, 'quantity': 2},  # 300g * 2 = 600g
        {'book_id': 2, 'quantity': 1},  # No weight
        {'book_id': 3, 'quantity': 5},  # 100g * 5 = 500g
    ]
    # 600 + 0 + 500 = 1100g = 1.1kg
    assert calculate_total_weight(cart_items) == Decimal('1.1')


# Tests for calculate_shipping_with_melhor_envio
def test_calculate_shipping_success(mock_config, mock_requests_post, mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    mock_requests_post.return_value.json.return_value = [
        {'id': '1', 'name': 'Option A', 'price': 10.0},
        {'id': '2', 'name': 'Option B', 'price': 15.0},
    ]
    mock_requests_post.return_value.raise_for_status.return_value = None

    cart = {'book_id_1': {'quantity': 1}}
    zip_code = '98765-432'
    shipping_options = calculate_shipping_with_melhor_envio(cart, zip_code)

    assert len(shipping_options) == 2
    assert shipping_options[0]['name'] == 'Option A'
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert kwargs['json']['to']['postal_code'] == zip_code
    assert kwargs['json']['package']['weight'] == 0.5  # 500g / 1000 = 0.5kg
    assert kwargs['json']['package']['width'] == DEFAULT_PACKAGE_DIMENSIONS['width']


def test_calculate_shipping_no_options_found(mock_config, mock_requests_post, mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    mock_requests_post.return_value.json.return_value = [
        {'error': 'Some error', 'id': 'error_id'}
    ]  # Simulate only error options
    mock_requests_post.return_value.raise_for_status.return_value = None

    cart = {'book_id_1': {'quantity': 1}}
    zip_code = '98765-432'

    with pytest.raises(Exception, match=f"Erro ao calcular Frete: Nenhuma op\u00e7\u00e3o de frete encontrada para este CEP - {zip_code}"):
        calculate_shipping_with_melhor_envio(cart, zip_code)


def test_calculate_shipping_request_exception(mock_config, mock_requests_post, mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    mock_requests_post.side_effect = requests.RequestException("Network error")

    cart = {'book_id_1': {'quantity': 1}}
    zip_code = '98765-432'

    with pytest.raises(Exception, match='Falha na requisição da API Melhor Envio: Network error'):
        calculate_shipping_with_melhor_envio(cart, zip_code)


def test_calculate_shipping_general_exception(mock_config, mock_requests_post, mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    mock_requests_post.return_value.json.side_effect = Exception("Invalid JSON")

    cart = {'book_id_1': {'quantity': 1}}
    zip_code = '98765-432'

    with pytest.raises(Exception, match='Erro ao calcular Frete: Invalid JSON'):
        calculate_shipping_with_melhor_envio(cart, zip_code)


def test_calculate_shipping_with_shipping_option_in_cart(mock_config, mock_requests_post, mock_book_model):
    mock_book_model.return_value = MagicMock(weight_g=Decimal('500'))
    mock_requests_post.return_value.json.return_value = [
        {'id': '1', 'name': 'Option A', 'price': 10.0},
    ]
    mock_requests_post.return_value.raise_for_status.return_value = None

    cart = {'book_id_1': {'quantity': 1}, 'shipping_option': 'some_option_id'}
    zip_code = '98765-432'
    shipping_options = calculate_shipping_with_melhor_envio(cart, zip_code)

    assert len(shipping_options) == 1
    mock_requests_post.assert_called_once()
    # Ensure 'shipping_option' is not part of the items sent for weight calculation
    args, kwargs = mock_requests_post.call_args
    assert 'shipping_option' not in kwargs['json']['package']
    assert kwargs['json']['package']['weight'] == 0.5
