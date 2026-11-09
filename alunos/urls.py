from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

urlpatterns = [
    path(
        "painel/",
        views.painel_inicial,
        name="painel_inicial",
    ),

    path(
        "",
        views.listar_alunos,
        name="listar_alunos",
    ),

    # --------------------------------------------------------
    # CADASTRO E GERENCIAMENTO DE ALUNOS
    # --------------------------------------------------------

    path(
        "alunos/novo/",
        views.cadastrar_aluno,
        name="cadastrar_aluno",
    ),

    path(
        "alunos/<int:aluno_id>/editar/",
        views.editar_aluno,
        name="editar_aluno",
    ),

    path(
        "alunos/<int:aluno_id>/status/",
        views.alternar_status_aluno,
        name="alternar_status_aluno",
    ),

    # --------------------------------------------------------
    # CATRACA E HISTÓRICO DE ACESSOS
    # --------------------------------------------------------

    path(
        "catraca/",
        views.simular_catraca,
        name="simular_catraca",
    ),

    path(
        "historico/",
        views.historico_acessos,
        name="historico_acessos",
    ),

    # --------------------------------------------------------
    # AUTENTICAÇÃO
    # --------------------------------------------------------

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="alunos/login.html",
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # --------------------------------------------------------
    # PAGAMENTOS
    # --------------------------------------------------------

    path(
        "pagamentos/",
        views.pagamentos,
        name="pagamentos",
    ),
]