from django.db import models
from django.conf import settings
# Create your models here.

class AddressModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        )
    zip_code = models.CharField('CEP', max_length=9)
    street = models.CharField('Rua', max_length=250)
    number = models.CharField('Numero', max_length=20) # O numero da rua pode ser ALFANUMERICO! 
    complement = models.CharField('Complemento', max_length=250, blank=True, null=True, help_text='Ex: apto 33')
    neighborhood = models.CharField('Bairro', max_length=250)
    city = models.CharField('Cidade', max_length=150)
    state = models.CharField('Estado', max_length=2, help_text='Sigla do Estado, ex: RS, SC, SP, etc.')
    country = models.CharField('País', max_length=50, default='Brasil')
    is_primary = models.BooleanField('Endereço Principal', default=False, help_text='É seu endereço principal?')
