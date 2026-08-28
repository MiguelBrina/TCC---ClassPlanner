from django.conf import settings
from django.db import models


class Professor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professor"
    )

    nome_exibicao = models.CharField(
        max_length=100,
        blank=True
    )

    agenda_configurada = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.nome_exibicao or self.usuario.first_name or self.usuario.email

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"


class DisponibilidadeProfessor(models.Model):

    DIAS_SEMANA = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="disponibilidades"
    )

    dia_semana = models.PositiveSmallIntegerField(
        choices=DIAS_SEMANA
    )

    hora_inicio = models.TimeField()

    hora_fim = models.TimeField()

    class Meta:
        ordering = ["dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "professor",
                    "dia_semana",
                    "hora_inicio",
                    "hora_fim"
                ],
                name="unique_disponibilidade_professor"
            )
        ]

    def __str__(self):
        return (
            f"{self.professor} - "
            f"{self.get_dia_semana_display()} - "
            f"{self.hora_inicio} às {self.hora_fim}"
        )