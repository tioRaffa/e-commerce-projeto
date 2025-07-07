from rest_framework import serializers
from orders.models import OrderModel
from .order_item_serializer import OrderItemReadSerializer, OrderItemCreateSerializer
from addresses.serializer import AddressSerializer
from addresses.models import AddressModel
from rest_framework.exceptions import ValidationError


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    final_total = serializers.ReadOnlyField()
    user = serializers.StringRelatedField()
    address = AddressSerializer(read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            'id',
            'user',
            'status',
            'final_total',
            'shipping_cost',
            'shipping_method',
            'tracking_code',
            'address',
            'created_at',
            'items',
        ]


class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(
        required=True,
        write_only=True,
        help_text="ID do endereço de entrega selecionado pelo usuário."
    )
    shipping_method = serializers.CharField(
        required=True, 
        write_only=True,
        help_text="Metodo de envio escolhido (ex: 'SEDEX')."
    )
    payment_method_id = serializers.CharField(
        required=True,
        write_only=True,
        help_text="ID do Método de Pagamento gerado pelo Stripe.js (ex: pm_...)"
    )
    

    def validate_address_id(self, value):
        user = self.context['request'].user
        try:
            address = AddressModel.objects.get(pk=value, user=user)
        except AddressModel.DoesNotExist:
              raise serializers.ValidationError("Endereço inválido ou não pertence a este usuário.")
        return address
    
    