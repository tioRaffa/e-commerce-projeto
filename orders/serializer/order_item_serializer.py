from rest_framework import serializers
from orders.models import OrderItemModel
from books.serializers import BookSerializer
from books.models import BookModel
from rest_framework.exceptions import ValidationError



class OrderItemReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItemModel
        fields = [
            'book',
            'quantity',
            'price_at_purchase',
            'total_price'
        ]

class OrderItemCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True, min_value=1)

    def validate_book_id(self, value):
        if not BookModel.objects.filter(
            pk=value, is_active=True
        ).exists():
            raise ValidationError(
                'Livro não encotrado ou Inativo'
            )
        return value