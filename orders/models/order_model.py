from django.db import models
from django.conf import settings
from addresses.models import AddressModel

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class OrderModel(Base):
    class OrderStatus(models.TextChoices):
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Aguardando Pagamento'
        PROCESSING = 'PROCESSING', 'Processando'
        SHIPPED = 'SHIPPED', 'Enviado'
        DELIVERED = 'DELIVERED', 'Entregue'
        CANCELED = 'CANCELED', 'Cancelado'
        FAILED = 'FAILED', 'Falhou'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario',
        related_name='orders'
    )
    address = models.ForeignKey(
        AddressModel,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Endereço de Entrega"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_PAYMENT,
        verbose_name='Status do Pedido'
    )

    # Financeiro
    total_items_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço Total dos Itens'
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Custo do Frete'
    )

    # Melhor Envio
    shipping_method = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Metodo de Envio (ex: SEDEX)"
    )
    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Codigo de Rastreio"
    )
    melhor_envio_order_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID do Pedido no Melhor Envio"
    )

    # Abacate Pay
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Metodo de Pagamento'
    )
    payment_charge_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        verbose_name='ID de transação -AbacatePay-'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido {self.id} - {self.user.username if self.user else 'Usuário Removido'}"

    @property
    def final_total(self):
        return self.total_items_price + self.shipping_cost

