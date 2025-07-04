import stripe
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from orders.models import *
import stripe.error

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
    ...
    ...
    ...

