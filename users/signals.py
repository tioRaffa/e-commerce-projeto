from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ProfileModel


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        ProfileModel.objects.create(user=instance)