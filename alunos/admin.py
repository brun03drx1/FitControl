from django.contrib import admin

from .models import (
    Aluno,
    RegistroAcesso,
    Plano,
    Pagamento,
)


# ============================================================
# ADMINISTRAÇÃO DE ALUNOS
# ============================================================

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        "matricula",
        "nome",
        "telefone",
        "validade",
        "ativo",
    )

    search_fields = (
        "matricula",
        "nome",
        "telefone",
    )

    list_filter = (
        "ativo",
        "validade",
    )


# ============================================================
# ADMINISTRAÇÃO DE REGISTROS DE ACESSO
# ============================================================

@admin.register(RegistroAcesso)
class RegistroAcessoAdmin(admin.ModelAdmin):
    list_display = (
        "matricula_informada",
        "aluno",
        "autorizado",
        "motivo",
        "data_hora",
    )

    search_fields = (
        "matricula_informada",
        "aluno__nome",
    )

    list_filter = (
        "autorizado",
        "data_hora",
    )

    readonly_fields = (
        "aluno",
        "matricula_informada",
        "autorizado",
        "motivo",
        "data_hora",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================================
# ADMINISTRAÇÃO DE PLANOS
# ============================================================

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "valor",
        "duracao_dias",
        "ativo",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
    )


# ============================================================
# ADMINISTRAÇÃO DE PAGAMENTOS
# ============================================================

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "aluno",
        "valor",
        "data_pagamento",
        "competencia",
        "forma_pagamento",
    )

    list_filter = (
        "forma_pagamento",
        "data_pagamento",
        "competencia",
    )

    search_fields = (
        "aluno__nome",
        "aluno__matricula",
    )

    date_hierarchy = "data_pagamento"