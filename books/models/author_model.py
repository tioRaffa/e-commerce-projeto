from django.db import models


class AuthorModel(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name