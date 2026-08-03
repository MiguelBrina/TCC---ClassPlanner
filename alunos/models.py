from django.db import models

class Aluno(models.model):

    nome_completo = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    data_inicio = models.DateField()

    def __str__(self):
        return self.nome_completo

    class Meta:
        ordering = ['nome_completo']
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
