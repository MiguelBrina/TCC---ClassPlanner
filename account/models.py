from django.conf import settings
from django.db import models


class Professor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professor"
    )
    
    def __str__(self):
        return self.usuario.first_name or self.usuario.email

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"