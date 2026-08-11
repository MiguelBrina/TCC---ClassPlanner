from django.db import models
from account.models import Professor
#region hierarquia de ensino 
class Disciplina(models.Model):
    professor = models.ForeignKey(
        "account.Professor",
        on_delete=models.CASCADE,
        related_name="disciplinas"
    )
    
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Tema(models.Model):
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="temas"
    )

    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Conteudo(models.Model):
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name="conteudos"
    )

    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome

#endregion

#region alunos
class Aluno(models.Model):
    professor = models.ForeignKey(
        "account.Professor",
        on_delete=models.CASCADE,
        related_name="alunos"
    )
     
    nome_completo = models.CharField(max_length=150, null=False, blank = False)
    telefone = models.CharField(max_length=20)
   

    def __str__(self):
        return self.nome_completo

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
#endregion

#region agenda do professor 
class Aula(models.Model):
    professor = models.ForeignKey(
        "account.Professor",
        on_delete=models.CASCADE,
        related_name="aulas"
    )

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name="aulas"
    )

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="aulas"
    )

    data = models.DateField()
    horario = models.TimeField()

    def __str__(self):
        return f"{self.aluno} - {self.disciplina} - {self.data} {self.horario}"

#endregion

#region registros de aula
class DiarioDeBordo(models.Model):
    matricula = models.OneToOneField(
        Matricula,
        on_delete=models.CASCADE,
        related_name="diario"
    )

    def __str__(self):
        return f"Diário - {self.matricula}"

class Registro(models.Model):
    diario = models.ForeignKey(
        DiarioDeBordo,
        on_delete=models.CASCADE,
        related_name="registros"
    )

    data = models.DateField()
    observacao = models.TextField(blank=True)

    temas = models.ManyToManyField(
        Tema,
        blank=True,
        related_name="registros"
    )

    conteudos = models.ManyToManyField(
        Conteudo,
        blank=True,
        related_name="registros"
    )

    def __str__(self):
        return f"Registro {self.data}"

    class Meta:
        ordering = ["-data"]
#endregion

#region modelo de checagem de pagamentos
class Pagamento(models.Model):
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name="pagamentos"
    )

    mes = models.DateField()

    pago = models.BooleanField(default=False)

    def __str__(self):
        status = "Pago" if self.pago else "Pendente"
        return f"{self.aluno} - {self.mes:%m/%Y} - {status}"

#endregion