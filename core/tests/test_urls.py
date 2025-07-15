
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from books.models.book_model import BookModel
from orders.models.order_model import OrderModel
from orders.models.order_item_model import OrderItemModel
from addresses.models import AddressModel
from unittest.mock import patch

@pytest.mark.django_db
def test_admin_url(api_client):
    url = reverse('admin:index')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_302_FOUND  # Redirects to login

@pytest.mark.django_db
def test_user_list_url(api_client, authenticated_user):
    url = reverse('user-api-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_address_list_url(api_client, authenticated_user):
    url = reverse('address-api-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_book_list_url(api_client):
    url = reverse('book-api-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_order_list_url(api_client, authenticated_user):
    url = reverse('order-api-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_cart_list_url(api_client, authenticated_user):
    url = reverse('cart-api')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@patch('orders.services.melhor_envio.calculate_shipping_with_melhor_envio')
def test_shipping_options_url(mock_calculate_shipping, api_client, authenticated_user):
    mock_calculate_shipping.return_value = [{'name': 'PAC', 'price': 10.00}]

    address = AddressModel.objects.create(user=authenticated_user, street='Test Street', city='Test City', state='TS', zip_code='12345-678', number='123', neighborhood='Test Neighborhood')
    book = BookModel.objects.create(title='Test Book for Shipping', price=20.00)
    cart_data = {'items': {str(book.pk): {'quantity': 1, 'price': float(book.price), 'title': book.title}}}
    
    session = api_client.session
    session['cart'] = cart_data
    session.save()

    data = {'address_id': address.pk}
    url = reverse('shipping-options')
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.fixture
def authenticated_user(api_client):
    user = User.objects.create_superuser(email='testuser@example.com', password='password123', username='testuser')
    api_client.force_authenticate(user=user)
    return user
