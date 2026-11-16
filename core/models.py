from django.db import models




#region hierarquia de ensino

class Disciplina(models.Model):
    professor = models.ForeignKey(
        "conta.Professor",
        on_delete=models.CASCADE,
        related_name="disciplinas",
    )

    nome = models.CharField(max_length=100)

    cor = models.CharField(
        max_length=7,
        default="#3b82f6",
    )

    def __str__(self):
        return self.nome

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["professor", "nome"],
                name="unique_disciplina_professor_nome",
            ),
        ]


class Tema(models.Model):
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="temas",
    )

    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["disciplina", "nome"],
                name="unique_tema_disciplina_nome",
            ),
        ]


class Conteudo(models.Model):
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name="conteudos",
    )

    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tema", "nome"],
                name="unique_conteudo_tema_nome",
            ),
        ]

#endregion
#region alunos
class Aluno(models.Model):
    professor = models.ForeignKey(
        "conta.Professor",
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "disciplina"],
                name="unique_matricula_aluno_disciplina",
            ),
        ]

#region agenda do professor 
class Aula(models.Model):
    professor = models.ForeignKey(
        "conta.Professor",
        on_delete=models.CASCADE,
        related_name="aulas"
    )

     # Bloco semanal da agenda em que esta aula acontece.
    # OneToOneField garante que um bloco não receba duas aulas.
    # null=True mantém compatibilidade com aulas antigas.
    disponibilidade = models.OneToOneField(
        "conta.DisponibilidadeProfessor",
        on_delete=models.PROTECT,
        related_name="aula",
        null=True,
        blank=True,
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

    # Campos antigos, mantidos temporariamente para preservar
    # compatibilidade com os registros de aulas anteriores.
    data = models.DateField(
        null=True,
        blank=True,
    )

    horario = models.TimeField(
        null=True,
        blank=True,
    )
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

class Auditoria(models.Model):
    OPERACOES = [
        ("INSERT", "Inserção"),
        ("UPDATE", "Atualização"),
        ("DELETE", "Exclusão"),
    ]

    professor_id = models.IntegerField(null=True, blank=True)
    tabela = models.CharField(max_length=100)
    registro_id = models.IntegerField()
    operacao = models.CharField(max_length=10, choices=OPERACOES)
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Auditoria"
        verbose_name_plural = "Auditorias"
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.tabela} - {self.operacao} - {self.data_hora}"
