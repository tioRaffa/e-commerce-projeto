from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from orders.models import OrderModel
from orders.serializer import OrderReadSerializer, OrderCreateSerializer
from decimal import Decimal
from orders.services.stripe import create_order_from_cart



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
            print("=========================================================")
            print(">>> ERRO DE INTEGRIDADE DO BANCO CAPTURADO <<<")
            print(f"TIPO DA EXCEÇÃO: {type(e)}")
            print(f"MENSAGEM COMPLETA DO ERRO: {e}")
            print("=========================================================")
            return Response({
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as e:
            # ESTE PRINT É A NOSSA FERRAMENTA DE DEPURAÇÃO
            print("=========================================================")
            print(">>> ERRO DE INTEGRIDADE DO BANCO CAPTURADO <<<")
            print(f"TIPO DA EXCEÇÃO: {type(e)}")
            print(f"MENSAGEM COMPLETA DO ERRO: {e}")
            print("=========================================================")
            
            return Response(
                {"detail": "Erro ao salvar no banco: um valor é muito longo ou uma chave única foi duplicada."},
                status=status.HTTP_400_BAD_REQUEST
            )