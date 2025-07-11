from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from orders.models import OrderModel
from orders.serializer import OrderReadSerializer, OrderCreateSerializer
from orders.services.stripe_service import create_order_from_cart, cancel_order_serivice



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
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        cart = request.session.get('cart', {})
        if not cart:
            return Response({
                'detail': 'Seu carrinho esta vazio.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            order = create_order_from_cart(
                user=request.user,
                cart=cart,
                validated_data=validated_data
            )
            del request.session['cart']

            read_serializer = OrderReadSerializer(order, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        
        except (ValueError, Exception) as e:
            return Response({
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as e:
            return Response(
                {"detail": "Erro ao salvar no banco: um valor é muito longo ou uma chave única foi duplicada."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        if order.status != OrderModel.OrderStatus.PROCESSING:
            return Response({
                'detail': f"Não é possivel cancelar um pedido com o status '{order.get_status_display()}'. "
            }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cancel_order_serivice(order)
            
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)