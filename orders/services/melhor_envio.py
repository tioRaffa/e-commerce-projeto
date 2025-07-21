import requests
from decouple import config
from decimal import Decimal

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