from rest_framework import viewsets
from orders.models import OrderModel
from common.permissions import IsOwenerAuth
from orders.serializer import OrderReadSerializer, OrderCreateSerializer



class OrderViewSet(viewsets.ModelViewSet):
    queryset = OrderModel.objects.all()
    permission_classes = [IsOwenerAuth]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'address'
        ).prefetch_related(
            'items__book'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer