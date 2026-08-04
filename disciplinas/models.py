from django.db import models

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"


class Materia(models.Model):
    disciplina = models.ForeignKey(
        'Disciplina',
        on_delete=models.CASCADE,
        related_name="materias"
    )

    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]
        verbose_name = "Matéria"
        verbose_name_plural = "Matérias"

class Conteudo(models.Model):

    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name="conteudos"
    )

    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]