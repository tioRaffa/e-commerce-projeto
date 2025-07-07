import stripe
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from orders.models import *
import stripe.error

from orders.models import OrderItemModel, OrderModel
from books.models import BookModel

def process_payment_with_stripe(amount: Decimal, payment_method_id: str) -> stripe.PaymentIntent:
    amount_in_cents = int(amount * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='brl',
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        )

        if intent.status != 'succeeded':
            raise Exception('Pagamento não foi concluido.')
        return intent

    except stripe.error.CardError as e:
        raise ValueError(f'Pagamento Recusado: {e.error.message}')
    except Exception as e:
        raise Exception(f"Erro ao processar o pagamento: {str(e)}")
    

def create_order_from_cart(user, cart: dict, validated_data: dict) -> OrderModel:
    address = validated_data.get('address')
    shipping_method = validated_data.get('shipping_method')
    payment_method_id = validated_data.get('payment_method_id')
    
    # Melhor Envio
    shipping_cost = Decimal('20.00') # Valor de exemplo

    total_items_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    final_total = total_items_price + shipping_cost
    
    payment_intent = process_payment_with_stripe(
        amount=final_total,
        payment_method_id=payment_method_id
    )
    

    with transaction.atomic():
        order = OrderModel.objects.create(
            user=user,
            address=address,
            shipping_address=f'{address.street}, {address.number}, {address.city}',
            status=OrderModel.OrderStatus.PROCESSING,
            total_items_price=total_items_price,
            shipping_cost=shipping_cost,
            shipping_method=shipping_method,
            stripe_payment_intent_id=payment_intent.id
        )


    order_items_to_create = []
    books_to_update = []

    for book_id_str, item_data in cart.items():
        book = get_object_or_404(BookModel, pk=int(book_id_str))
        if book.stock < item_data['quantity']:
            raise ValueError(
                f'Estoque insuficiente para o livro - {book.title}'
            )
        
        order_items_to_create.append(
            OrderItemModel(
                order=order,
                book=book,
                book_title_snapshot=item_data['title'],
                quantity=item_data['quantity'],
                price_at_purchase=item_data['price']
            )
        )
        book.stock -= item_data['quantity']
        books_to_update.append(book)

    OrderItemModel.objects.bulk_create(
        order_items_to_create
    )
    BookModel.objects.bulk_update(
        books_to_update, ['stock']
    )

    # -> sendgrid

    return order
