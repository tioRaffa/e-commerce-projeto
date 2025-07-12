
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from books.models.book_model import BookModel
from orders.models.order_model import OrderModel
from orders.models.order_item_model import OrderItemModel

@pytest.mark.django_db
def test_admin_url(client):
    url = reverse('admin:index')
    response = client.get(url)
    assert response.status_code == status.HTTP_302_FOUND  # Redirects to login

@pytest.mark.django_db
def test_user_list_url(client, authenticated_user):
    url = reverse('user-api-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_address_list_url(client, authenticated_user):
    url = reverse('address-api-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_book_list_url(client):
    url = reverse('book-api-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_order_list_url(client, authenticated_user):
    url = reverse('order-api-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_cart_list_url(client, authenticated_user):
    url = reverse('cart-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_cart_detail_url(client, authenticated_user):
    book = BookModel.objects.create(title='Test Book', price=10.00)
    order = OrderModel.objects.create(user=authenticated_user, total_items_price=10.00, shipping_cost=0.00)
    order_item = OrderItemModel.objects.create(order=order, book=book, quantity=1, price_at_purchase=10.00, book_title_snapshot='Test Book')
    url = reverse('cart-detail', kwargs={'pk': order_item.pk})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_shipping_options_url(client, authenticated_user):
    url = reverse('shipping-options')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.fixture
def authenticated_user(client):
    user = User.objects.create_superuser(email='testuser@example.com', password='password123', username='testuser')
    client.login(email='testuser@example.com', password='password123')
    return user
