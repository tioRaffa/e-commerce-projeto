from django.conf import settings
from .base import BaseModel
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class ProfileModel(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    cpf = models.CharField('CPF', max_length=14, unique=True, blank=True, help_text='Identidade do Usuario')
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    phone_number = PhoneNumberField('Número de Telefone', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Peril de {self.user.username}"