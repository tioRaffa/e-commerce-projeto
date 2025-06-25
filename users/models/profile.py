from django.db import models
from django.conf import settings

class ProfileModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True, blank=True)

    def __str__(self):
        return f"Peril de {self.user.username}"