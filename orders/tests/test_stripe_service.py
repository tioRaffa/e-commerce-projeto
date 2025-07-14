import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

import stripe
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404

from books.models import BookModel
from addresses.models import AddressModel
from orders.models import OrderModel, OrderItemModel

from orders.services.stripe_service import (
    process_payment_with_stripe,
    create_order_from_cart,
    refound_stripe_payment,
    cancel_order_service,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', email='test@example.com')


@pytest.fixture
def address(user):
    return AddressModel.objects.create(user=user, zip_code='88000000', street='Rua Teste', number='123', city='Cidade Teste', state='TS')


@pytest.fixture
def book():
    return BookModel.objects.create(title='Livro de Teste', price='50.00', stock=10, weight_g=500)


@pytest.fixture
def cart(book):
    return {
        'items': {
            str(book.id): {
                'quantity': 2,
                'price': '50.00',
                'title': book.title
            }
        },
        'shipping_option': {
            'name': 'SEDEX',
            'price': Decimal('25.00')
        }
    }


@pytest.fixture
def validated_data(address):
    return {
        'address_id': address,
        'payment_method_id': 'pm_card_visa'
    }


# Tests for process_payment_with_stripe
@patch('stripe.PaymentIntent.create')
def test_process_payment_with_stripe_success(mock_create):
    mock_intent = MagicMock(id='pi_123', status='succeeded')
    mock_create.return_value = mock_intent

    amount = Decimal('100.00')
    payment_method_id = 'pm_card_visa'

    result = process_payment_with_stripe(amount, payment_method_id)

    mock_create.assert_called_once_with(
        amount=10000,
        currency='brl',
        payment_method=payment_method_id,
        confirm=True,
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )
    assert result == mock_intent


@patch('stripe.PaymentIntent.create')
def test_process_payment_with_stripe_card_error(mock_create):
    mock_create.side_effect = stripe.error.CardError(
        message='Your card was declined.', code='card_declined', param=None,
        json_body={'error': {'message': 'Your card was declined.'}}
    )

    amount = Decimal('100.00')
    payment_method_id = 'pm_card_visa'

    with pytest.raises(ValueError, match='Pagamento Recusado: Your card was declined.'):
        process_payment_with_stripe(amount, payment_method_id)


@patch('stripe.PaymentIntent.create')
def test_process_payment_with_stripe_general_exception(mock_create):
    mock_create.side_effect = Exception('Network error')

    amount = Decimal('100.00')
    payment_method_id = 'pm_card_visa'

    with pytest.raises(Exception, match='Erro ao processar o pagamento: Network error'):
        process_payment_with_stripe(amount, payment_method_id)


@patch('stripe.PaymentIntent.create')
def test_process_payment_with_stripe_not_succeeded(mock_create):
    mock_intent = MagicMock(id='pi_123', status='requires_action')
    mock_create.return_value = mock_intent

    amount = Decimal('100.00')
    payment_method_id = 'pm_card_visa'

    with pytest.raises(Exception, match='Pagamento não foi concluido.'):
        process_payment_with_stripe(amount, payment_method_id)


# Tests for create_order_from_cart
@patch('orders.services.stripe_service.process_payment_with_stripe')
@patch('orders.services.stripe_service.get_object_or_404')
def test_create_order_success(mock_get_object_or_404, mock_process_payment, user, cart, validated_data, book):
    mock_get_object_or_404.return_value = book

    mock_payment_intent = MagicMock(id='pi_12345_success', status='succeeded')
    mock_process_payment.return_value = mock_payment_intent

    order = create_order_from_cart(user=user, cart=cart, validated_data=validated_data)

    assert order.status == OrderModel.OrderStatus.PROCESSING
    assert order.stripe_payment_intent_id == 'pi_12345_success'
    assert order.items.count() == 1
    
    
    


@patch('orders.services.stripe_service.process_payment_with_stripe')
def test_create_order_payment_fails(mock_process_payment, user, cart, validated_data, book):
    mock_process_payment.side_effect = ValueError("Pagamento recusado pelo emissor.")

    with pytest.raises(ValueError, match="Pagamento recusado pelo emissor."):
        create_order_from_cart(user=user, cart=cart, validated_data=validated_data)

    assert OrderModel.objects.count() == 0
    
    book.refresh_from_db()
    assert book.stock == 10


def test_create_order_insufficient_stock(user, cart, validated_data, book):
    book.stock = 1
    book.save()

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        create_order_from_cart(user=user, cart=cart, validated_data=validated_data)

    assert OrderModel.objects.count() == 0


def test_create_order_no_shipping_option(user, cart, validated_data):
    cart_no_shipping = cart.copy()
    del cart_no_shipping['shipping_option']

    with pytest.raises(ValueError, match='Nenhum metodo de envio selecionado, Por favor.. Calcule o Frete Primeiro'):
        create_order_from_cart(user=user, cart=cart_no_shipping, validated_data=validated_data)

    assert OrderModel.objects.count() == 0


# Tests for refound_stripe_payment
@patch('stripe.Refund.create')
def test_refound_stripe_payment_success(mock_create):
    payment_intent_id = 'pi_refund_test'
    refound_stripe_payment(payment_intent_id)
    mock_create.assert_called_once_with(payment_intent=payment_intent_id)


@patch('stripe.Refund.create')
def test_refound_stripe_payment_failure(mock_create):
    mock_create.side_effect = Exception('Refund failed')
    payment_intent_id = 'pi_refund_test'

    with pytest.raises(Exception, match='Falha ao estornar o pagamento no Stripe: Refund failed'):
        refound_stripe_payment(payment_intent_id)


# Tests for cancel_order_service
@patch('orders.services.stripe_service.refound_stripe_payment')
def test_cancel_order_success(mock_refound_payment, user, address, book):
    book.stock = 8
    book.save()
    order = OrderModel.objects.create(
        user=user, address=address, status=OrderModel.OrderStatus.PROCESSING,
        stripe_payment_intent_id='pi_12345_success',
        total_items_price=100, shipping_cost=20
    )
    OrderItemModel.objects.create(order=order, book=book, quantity=2, price_at_purchase=50)

    cancel_order_service(order=order)

    order.refresh_from_db()
    book.refresh_from_db()
    
    assert order.status == OrderModel.OrderStatus.CANCELED
    assert book.stock == 10
    mock_refound_payment.assert_called_once_with('pi_12345_success')


def test_cancel_order_no_payment_intent_id(user, address, book):
    order = OrderModel.objects.create(
        user=user, address=address, status=OrderModel.OrderStatus.PENDING_PAYMENT,
        total_items_price=100, shipping_cost=20
    )
    OrderItemModel.objects.create(order=order, book=book, quantity=2, price_at_purchase=50)

    with pytest.raises(ValueError, match='Este pedido não possui um ID de pagamento para estornar.'):
        cancel_order_service(order=order)

    order.refresh_from_db()
    assert order.status == OrderModel.OrderStatus.PENDING_PAYMENT


@patch('orders.services.stripe_service.refound_stripe_payment')
def test_cancel_order_refund_failure(mock_refound_payment, user, address, book):
    mock_refound_payment.side_effect = Exception('Refund failed during cancellation')

    book.stock = 8
    book.save()
    order = OrderModel.objects.create(
        user=user, address=address, status=OrderModel.OrderStatus.PROCESSING,
        stripe_payment_intent_id='pi_12345_success',
        total_items_price=100, shipping_cost=20
    )
    OrderItemModel.objects.create(order=order, book=book, quantity=2, price_at_purchase=50)

    with pytest.raises(Exception, match='Refund failed during cancellation'):
        cancel_order_service(order=order)

    order.refresh_from_db()
    book.refresh_from_db()
    assert order.status == OrderModel.OrderStatus.PROCESSING # Status should not change
    assert book.stock == 8 # Stock should still be reverted