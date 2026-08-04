from django.contrib import admin

from .models import Disciplina
from .models import Materia
from .models import Conteudo

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        
    )

    search_fields = (
        "nome",
    )

    ordering = (
        "nome",
    )
admin.site.register(Materia)
admin.site.register(Conteudo)