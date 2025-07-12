import requests
from decouple import config
from decimal import Decimal

DEFAULT_PACKAGE_DIMENSIONS = {
    "width": 16,
    "height": 23,
    "length": 5,
}

def calculate_total_weight(cart_items: list) -> Decimal:
    total_weight = Decimal('0')
    for item in cart_items:
        total_weight += Decimal('0.5') * item['quantity']
    return total_weight


def calculate_shipping_with_melhor_envio(cart: dict, zip_code: str) -> list:

    api_url = f'{config('ME_SANDBOX_URL')}/api/v2/me/shipment/calculate'
    token = config('ME_ACCESS_TOKEN')

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Bookstore API - Projeto Pessoal (rafaelmuniz200@gmail.com)"
        }

    items_to_calculate = cart.get('items') if cart.get('items') is not None else []
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

    except Exception as e: 
        raise Exception(f'Erro ao calcular Frete: {e}')
    except requests.RequestException as e:
        raise Exception(f'Falha na requisição da API Melhor Envio: {e}')