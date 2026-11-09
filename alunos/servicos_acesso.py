from django.utils import timezone

from .models import Aluno


# ============================================================
# VALIDAÇÃO DE ACESSO À CATRACA
# ============================================================

def validar_acesso(matricula):
    """
    Valida a matrícula e determina se o aluno pode entrar
    na academia.

    Retorna um dicionário com:
    - autorizado: True ou False
    - motivo: descrição do resultado
    - aluno: objeto Aluno ou None
    """

    matricula = (matricula or "").strip()

    # 1. Verifica se a matrícula foi informada.
    if not matricula:
        return {
            "autorizado": False,
            "motivo": "Informe a matrícula.",
            "aluno": None,
        }

    # 2. Busca o aluno pela matrícula.
    aluno = Aluno.objects.filter(
        matricula=matricula,
    ).first()

    # 3. Verifica se o aluno está cadastrado.
    if aluno is None:
        return {
            "autorizado": False,
            "motivo": "Aluno não cadastrado.",
            "aluno": None,
        }

    # 4. Verifica se o aluno está ativo.
    if not aluno.ativo:
        return {
            "autorizado": False,
            "motivo": "Aluno bloqueado ou inativo.",
            "aluno": aluno,
        }

    # 5. Verifica se a matrícula está dentro da validade.
    hoje = timezone.localdate()

    if aluno.validade < hoje:
        return {
            "autorizado": False,
            "motivo": "Matrícula vencida.",
            "aluno": aluno,
        }

    # 6. Todas as verificações foram aprovadas.
    return {
        "autorizado": True,
        "motivo": "Matrícula válida.",
        "aluno": aluno,
    }