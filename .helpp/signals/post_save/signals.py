
from django.db.models.signals import post_save
from django .contrib.auth.models import User

#                                       / -Classe User do django
class Profile:                       # /
    usuario = models.OnteToOneField(User, on_delete=models.CASCADE)
    telefone = ...

                                                               # ->sender: seria o usuario sendo criado
                                                               # ->instance: é o objeto que ta sendo criado\apagado\deletado
                                                               # -> created: É um boolean True quando for criado, False quando for alterado 
def cria_profile(sender, instance, created, **kwargs):      # ___/
    if created:
        Profile.objects.create(usuario=instance)

    else:                                                         # -> se for modificado e nao criado
        if not hasattr(instance, 'profile'):
            Profile.objects.create(usuario=instance)


post_save.connect(cria_profile, sender=User)   #-> QUANDO SALVAR UM OBJETO DO TIPO USER, 
#                       |                         SERA CHAMADO A FUNCAO cria_profile
#                   receiver:
#                     metodo que vai
#                        ser chamado


# APP
class AuthorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authors"

    def ready(self, *args, **kwargs):
        import authors.signals
        return super().ready(*args, **kwargs)