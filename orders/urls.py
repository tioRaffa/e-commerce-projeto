from django.urls import path
from orders.views import CartAPIView, ShippingOptions, CartShippingSelectionAPIView

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', CartAPIView.as_view(), name='cart-detail'),
    path('checkout/shipping-options/', ShippingOptions.as_view(), name='shipping-options'),
    path('cart/select-shipping/', CartShippingSelectionAPIView.as_view(), name='shipping-selected'),
]