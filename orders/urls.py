from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import CartAPIView, ShippingOptions, CartShippingSelectionAPIView, OrderViewSet


urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart-api'),
    path('checkout/shipping-options/', ShippingOptions.as_view(), name='shipping-options'),
    path('cart/select-shipping/', CartShippingSelectionAPIView.as_view(), name='cart-select-shipping'),
]