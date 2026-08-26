from django.db.models.signals import post_save
from django.dispatch import receiver

from allauth.socialaccount.models import SocialAccount

from .models import Professor


@receiver(post_save, sender=SocialAccount)
def criar_professor_conta_social(sender, instance, **kwargs):

    print("SIGNAL SOCIALACCOUNT:", instance.user)

    Professor.objects.get_or_create(
        usuario=instance.user
    )