import stripe
from decimal import Decimal

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