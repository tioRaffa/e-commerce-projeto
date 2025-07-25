from django.contrib import admin
from .models import OrderItemModel, OrderModel
# Register your models here.



@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_display',
        'address_zip_code',
        'total_items_price',
        'shipping_cost',
        'shipping_method',
        'final_total_display',
        'status',
        'created_at'
    ]
    search_fields = [
        'id',
        'user__first_name',
        'user__last_name',
        'user__email',
        'address__zip_code',
        'address__street',
    ]
    list_filter = [
        'status', 'created_at'
    ]
    list_per_page = 10
    ordering = ['-created_at']
    


    def get_list_display_links(self, request, list_display):
        return list_display

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'address')

    def user_display(self, obj):
        return f'{obj.user.first_name} - {obj.user.email}'
    user_display.short_description = 'Usuario'

    def final_total_display(self, obj):
        return f'R$ {obj.final_total:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    final_total_display.short_description = 'Preço Final'

    def address_zip_code(self, obj):
        return obj.address.zip_code
    address_zip_code.short_description = 'CEP'



@admin.register(OrderItemModel)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_id',
        'book',
        'quantity',
        'price_at_purchase',
        'total_price'
    ]
    search_fields = [
        'book__title', 'quantity', 'order__id'
    ]
    list_filter = [
        'order__status',
    ]
    list_per_page = 10
    ordering = ['-created_at']


    def get_list_display_links(self, request, list_display):
        return list_display

    def total_price(self, obj):
        return f'R$ {obj.total_price:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    total_price.short_description = 'Preço Total'

    def order_id(self, obj):
        return obj.order.id
    order_id.short_description = 'Id-Order'