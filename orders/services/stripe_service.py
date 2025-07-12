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
    address = validated_data.get('address_id')
    payment_method_id = validated_data.get('payment_method_id')

    shipping_info = cart.get('selected_shipping')
    if not shipping_info:
        raise ValueError('Nenhum metodo de envio selecionado, Por favor.. Calcule o Frete Primeiro')
    


    # Melhor Envio
    shipping_method = shipping_info.get('name')
    shipping_cost = Decimal(shipping_info.get('cost'))

    total_items_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    final_total = total_items_price + shipping_cost
   

    with transaction.atomic():
        order = OrderModel.objects.create(
            user=user,
            address=address,
            status=OrderModel.OrderStatus.PENDING_PAYMENT,
            total_items_price=total_items_price,
            shipping_cost=shipping_cost,
            shipping_method=shipping_method,
        )


        order_items_to_create = []
        books_to_update = []

        for book_id_str, item_data in cart.items():
            book = get_object_or_404(BookModel, pk=int(book_id_str))
            if book.stock < item_data['quantity']:
                raise ValueError(
                    f'Estoque insuficiente para o livro - {book.title}'
                )
            original_title = item_data.get('title', '')
                
            max_len = OrderItemModel._meta.get_field('book_title_snapshot').max_length
            truncated_title = (original_title[:max_len - 3] + '...') if len(original_title) > max_len else original_title
            
            order_items_to_create.append(
                OrderItemModel(
                    order=order,
                    book=book,
                    book_title_snapshot=truncated_title,
                    quantity=item_data['quantity'],
                    price_at_purchase=Decimal(item_data['price'])
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

        try:
            payment_intent = process_payment_with_stripe(
                amount=final_total,
                payment_method_id=payment_method_id
            )
            order.status = OrderModel.OrderStatus.PROCESSING
            order.stripe_payment_intent_id = payment_intent.id
            order.save(update_fields=['status', 'stripe_payment_intent_id', 'updated_at'])

            # SENDGRID pra sucesso

        except (ValueError, Exception) as e:
            order.status = OrderModel.OrderStatus.FAILED
            order.save(update_fields=['status', 'updated_at'])                

            # -> sendgrid pra falha
            raise e

    return order

def refound_stripe_payment(payment_intent_id: str):
    try:
        stripe.Refund.create(payment_intent=payment_intent_id)

    except Exception as e:
        raise Exception(f"Falha ao estornar o pagamento no Stripe: {str(e)}")


def cancel_order_service(order: OrderModel):
    if not order.stripe_payment_intent_id:
        raise ValueError('Este pedido não possui um ID de pagamento para estornar.')

    with transaction.atomic():
        for item in order.items.all():
            item.book.stock += item.quantity
            item.book.save(update_fields=['stock'])
        
        refound_stripe_payment(order.stripe_payment_intent_id)

        order.status = OrderModel.OrderStatus.CANCELED
        order.save(update_fields=['status', 'updated_at'])

        # sendgrid pra cancelar

