from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Professor


User = get_user_model()


@receiver(post_save, sender=User)
def criar_professor_usuario(sender, instance, created, **kwargs):
    if created:
        Professor.objects.get_or_create(
            usuario=instance
        )