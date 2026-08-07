from django.db import models


class DiarioDeBordo(models.Model):

    matricula = models.OneToOneField(
        'alunos.Matricula',
        on_delete=models.CASCADE,
        related_name="diario"
    )

    def __str__(self):
        return str(self.matricula)

    class Meta:
        verbose_name = "Diário de Bordo"
        verbose_name_plural = "Diários de Bordo"

class Registro(models.Model):

    diario = models.ForeignKey(
        'DiarioDeBordo',
        on_delete=models.CASCADE,
        related_name="registros"
    )

    data = models.DateField()

    observacao = models.TextField()

    materias = models.ManyToManyField(
        'disciplinas.Materia',
        blank=True
    )

    conteudos = models.ManyToManyField(
        'disciplinas.Conteudo',
        blank=True
    )

    def __str__(self):
        return f"Registro {self.data}"

    class Meta:
        ordering = ["-data"]