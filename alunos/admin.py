from django.contrib import admin
from .models import Aluno
from .models import Matricula


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        "nome_completo",
        "telefone",
        "data_inicio",
    )

    search_fields = (
        "nome_completo",
    )

    ordering = (
        "nome_completo",
    )

admin.site.register(Matricula)