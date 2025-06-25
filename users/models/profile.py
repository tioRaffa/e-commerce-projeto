from django.conf import settings
from .base import BaseModel
from django.db import models


class ProfileModel(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True, blank=True, help_text='Identidade do Usuario')

    def __str__(self):
        return f"Peril de {self.user.username}"