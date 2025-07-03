from django.db import models
from books.models import BookModel
from .order_model import Base, OrderModel


class OrderItemModel(Base):
    order = models.ForeignKey(
        OrderModel, 
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
        )
    book = models.ForeignKey(
        BookModel,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Livro'
        )
    
    book_title_snapshot = models.CharField(
        max_length=100,
        verbose_name='Titulo do Livro (no momento da compra)'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Quantidade'
    )
    price_at_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Preço (momento da compra)'
    )

    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens dos Pedidos'
    
    def __str__(self):
        return f'{self.quantity}x {self.book_title_snapshot} No Pedido #{self.order.pk}'
    
    @property
    def total_price(self):
        return self.quantity * self.price_at_purchase
