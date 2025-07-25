from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from addresses.models import AddressModel
from orders.services.melhor_envio import calculate_shipping_with_melhor_envio


class ShippingOptions(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address_id = request.data.get('address_id')
        cart = request.session.get('cart', {})

        if not address_id:
            return Response({
                'detail': 'O Id de endereço é obrigatorio'
            }, status=status.HTTP_400_BAD_REQUEST)
        cart_items = cart.get('items', {})
        if not cart_items:
            return Response({
                'detail': 'O carrinho esta vazio'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        address = get_object_or_404(AddressModel, pk=address_id, user=request.user)

        try:
            shipping_options = calculate_shipping_with_melhor_envio(
                cart=cart_items,
                zip_code=address.zip_code
            )
            return Response(
                shipping_options, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({
                'detail-erro': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)