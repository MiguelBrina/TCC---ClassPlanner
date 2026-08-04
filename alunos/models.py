from django.db import models
from disciplinas.models import Disciplina
class Aluno(models.Model):

    nome_completo = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    data_inicio = models.DateField()

    def __str__(self):
        return self.nome_completo

    class Meta:
        ordering = ['nome_completo']
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

class Matricula(models.Model):

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name="matriculas"
    )

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="matriculas"
    )

    data_inicio = models.DateField()

    def __str__(self):
        return f"{self.aluno} - {self.disciplina}"

    class Meta:
        ordering = ["aluno"]
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"