import requests
from decouple import config
from decimal import Decimal
from orders.models import OrderModel

DEFAULT_PACKAGE_DIMENSIONS = {
    "width": 16,
    "height": 23,
    "length": 5,
}


from books.models.book_model import BookModel

def calculate_total_weight(cart_items: list) -> Decimal:
    total_weight_grams = Decimal('0')
    for item in cart_items:
        book = BookModel.objects.get(pk=item['book_id'])
        if book.weight_g:
            total_weight_grams += book.weight_g * item['quantity']
    return total_weight_grams / 1000 


def calculate_shipping_with_melhor_envio(cart: dict, zip_code: str) -> list:
    base_url = config('ME_SANDBOX_URL')
    api_url = f'{base_url}/api/v2/me/shipment/calculate'
    token = config('ME_ACCESS_TOKEN')

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Bookstore API - Projeto Pessoal (rafaelmuniz200@gmail.com)"
        }

    items_to_calculate = [{**item_data, 'book_id': key} for key, item_data in cart.items() if key != 'shipping_option']
    total_weigth_kg = float(calculate_total_weight(items_to_calculate))

    payload = {
        "from": {
            "postal_code": config('MY_STORE_ZIP_CODE')
        },
        "to": {
            "postal_code": str(zip_code)
        },
        "package": {
            "weight": float(total_weigth_kg),
            **DEFAULT_PACKAGE_DIMENSIONS,
        }
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        shipping_options = [opt for opt in data if 'error' not in opt]
        if not shipping_options:
            raise ValueError(f"Nenhuma opção de frete encontrada para este CEP - {zip_code}")
        return shipping_options

    except requests.RequestException as e:
        raise Exception(f'Falha na requisição da API Melhor Envio: {e}')
    except Exception as e: 
        raise Exception(f'Erro ao calcular Frete: {e}')
    

def generate_shipping_label_service(order: OrderModel):
    if not order.shipping_service_id:
        raise ValueError(
            'O pedido deve conter um servico de frete selecionado'
        )
    
    base_url = config('ME_SANDBOX_URL')
    api_url = f'{base_url}/api/v2/me/cart'
    token = config('ME_ACCESS_TOKEN')

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Bookstore API - Projeto Pessoal (rafaelmuniz200@gmail.com)"
        }
    
    cart_payload = {
        "service": order.shipping_service_id,
        "from": { 
            "name": "Book Store",
            "phone": "48999998888",
            "email": "bookstoremail@loja.com",
            "document": "12.345.678/0001-95",
            "postal_code": config('MY_STORE_ZIP_CODE'),
            "address": "Rua lá da pqp",
            "number": "100"
        },
        "to": {
            "name": order.user.get_full_name(),
            "phone": str(order.address.user.profile.phone_number),
            "email": order.address.user.email,
            "document": order.address.user.profile.cpf,
            "postal_code": order.address.zip_code,
            "address": order.address.street,
            "number": order.address.number,
            "complement": order.address.complement,
            "neighborhood": order.address.neighborhood,
        },
        "products": [ # Lista de produtos do pedido
            {
                "name": item.book.title,
                "quantity": item.quantity,
                "unitary_value": float(item.price_at_purchase)
            } for item in order.items.all()
        ]
    }

    cart_response = requests.post(f'{api_url}', json=cart_payload, headers=headers)
    cart_response.raise_for_status()
    order_id_me = cart_response.json()['id']

    checkout_payload = {"orders": [order_id_me]}
    requests.post(f'{base_url}/api/v2/me/shipment/checkout', json=checkout_payload, headers=headers).raise_for_status()

    generate_payload = {"orders": [order_id_me]}
    generate_response = requests.post(f"{base_url}/api/v2/me/shipment/generate", json=generate_payload, headers=headers)
    generate_response.raise_for_status()   

    tracking_code = generate_payload.json()[order_id_me]['tracking']

    order.melhor_envio_order_id = order_id_me
    order.tracking_code = tracking_code
    order.status = OrderModel.OrderStatus.SHIPPED
    order.save(update_fields=['melhor_envio_order_id', 'tracking_code', 'status', 'updated_at'])

    return order