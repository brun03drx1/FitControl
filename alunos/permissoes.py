from django.contrib.auth.decorators import user_passes_test


# ============================================================
# VERIFICAÇÃO DE PERMISSÕES OPERACIONAIS
# ============================================================

def funcionario_autorizado(user):
    """
    Verifica se o usuário pode acessar as áreas operacionais
    do FitControl.

    O acesso é permitido para:
    - Superusuários.
    - Usuários pertencentes ao grupo
      'Funcionarios da Academia'.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(
        name="Funcionarios da Academia",
    ).exists()


# ============================================================
# DECORADOR DE PROTEÇÃO DAS PÁGINAS
# ============================================================

exigir_acesso_operacional = user_passes_test(
    funcionario_autorizado,
    login_url="login",
)