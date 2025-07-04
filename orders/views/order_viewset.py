from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from orders.models import OrderModel
from orders.serializer import OrderReadSerializer, OrderCreateSerializer
from decimal import Decimal
from orders.services.stripe import process_payment_with_stripe



class OrderViewSet(viewsets.ModelViewSet):
    queryset = OrderModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return self.request.user.orders.select_related(
            'address'
        ).prefetch_related(
            'items__book'
        ).order_by('-created_at')


    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer
    

    def get_cart_session(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return None
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        cart = self.get_cart_session(request)
        if cart is None:
            return Response({
                'detail': 'Seu carrinho esta vazio.'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        address = validated_data.get('address')

        try:
            # APi melhor envio
            shipping_cost = Decimal('15.10') # valor exemplo

            total_items_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
            
            final_total = total_items_price + shipping_cost
            payment_method_id = validated_data.get('payment_method_id')

            payment_intent = process_payment_with_stripe(
                amount=final_total,
                payment_method_id=payment_method_id
            )



        except:
            ...