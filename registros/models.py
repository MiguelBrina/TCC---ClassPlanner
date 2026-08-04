from django.db import models
from .models import Matricula
from .models import Materia
from .models import Conteudo

class DiarioDeBordo(models.Model):

    matricula = models.OneToOneField(
        Matricula,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.matricula)

class Registro(models.Model):

    diario = models.ForeignKey(
        DiarioDeBordo,
        on_delete=models.CASCADE,
        related_name="registros"
    )

    data = models.DateField()

    observacao = models.TextField()

materias = models.ManyToManyField(
    Materia,
    blank=True
)

conteudos = models.ManyToManyField(
    Conteudo,
    blank=True
)