from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.db import models, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import AlunoForm, PagamentoForm
from .models import Aluno, Mensalidade, Pagamento, RegistroAcesso
from .permissoes import exigir_acesso_operacional
from .servicos_acesso import validar_acesso


# ============================================================
# PAINEL PRINCIPAL
# ============================================================

@exigir_acesso_operacional
def painel_inicial(request):
    hoje = timezone.localdate()

    total_alunos = Aluno.objects.count()

    alunos_ativos = Aluno.objects.filter(
        ativo=True,
    ).count()

    matriculas_vencidas = Aluno.objects.filter(
        validade__lt=hoje,
    ).count()

    acessos_hoje = RegistroAcesso.objects.filter(
        data_hora__date=hoje,
    )

    total_acessos_hoje = acessos_hoje.count()

    acessos_liberados_hoje = acessos_hoje.filter(
        autorizado=True,
    ).count()

    acessos_bloqueados_hoje = acessos_hoje.filter(
        autorizado=False,
    ).count()

    ultimos_acessos = (
        RegistroAcesso.objects
        .select_related("aluno")
        .order_by("-data_hora")[:10]
    )

    contexto = {
        "total_alunos": total_alunos,
        "alunos_ativos": alunos_ativos,
        "matriculas_vencidas": matriculas_vencidas,
        "total_acessos_hoje": total_acessos_hoje,
        "acessos_liberados_hoje": acessos_liberados_hoje,
        "acessos_bloqueados_hoje": acessos_bloqueados_hoje,
        "ultimos_acessos": ultimos_acessos,
    }

    return render(
        request,
        "alunos/painel.html",
        contexto,
    )


# ============================================================
# GERENCIAMENTO DE ALUNOS
# ============================================================

@exigir_acesso_operacional
def listar_alunos(request):
    hoje = timezone.localdate()
    alunos = Aluno.objects.all()

    pesquisa = request.GET.get("q", "").strip()
    situacao = request.GET.get("situacao", "todos")

    if pesquisa:
        alunos = alunos.filter(
            models.Q(nome__icontains=pesquisa)
            | models.Q(matricula__icontains=pesquisa)
        )

    if situacao == "ativos":
        alunos = alunos.filter(
            ativo=True,
            validade__gte=hoje,
        )

    elif situacao == "bloqueados":
        alunos = alunos.filter(
            ativo=False,
        )

    elif situacao == "vencidos":
        alunos = alunos.filter(
            validade__lt=hoje,
        )

    contexto = {
        "alunos": alunos,
        "pesquisa": pesquisa,
        "situacao": situacao,
    }

    return render(
        request,
        "alunos/listar_alunos.html",
        contexto,
    )


@exigir_acesso_operacional
def cadastrar_aluno(request):
    if request.method == "POST":
        form = AlunoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("listar_alunos")

    else:
        form = AlunoForm()

    return render(
        request,
        "alunos/form_aluno.html",
        {
            "form": form,
            "titulo": "Cadastrar aluno",
        },
    )


@exigir_acesso_operacional
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
    )

    if request.method == "POST":
        form = AlunoForm(
            request.POST,
            instance=aluno,
        )

        if form.is_valid():
            form.save()
            return redirect("listar_alunos")

    else:
        form = AlunoForm(instance=aluno)

    return render(
        request,
        "alunos/form_aluno.html",
        {
            "form": form,
            "titulo": "Editar aluno",
        },
    )


@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="login",
)
def alternar_status_aluno(request, aluno_id):
    if request.method != "POST":
        return redirect("listar_alunos")

    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
    )

    aluno.ativo = not aluno.ativo

    aluno.save(
        update_fields=["ativo"],
    )

    return redirect("listar_alunos")


# ============================================================
# SIMULADOR DE CATRACA
# ============================================================

@exigir_acesso_operacional
def simular_catraca(request):
    resultado = None
    motivo = ""
    matricula = ""

    if request.method == "POST":
        matricula = request.POST.get(
            "matricula",
            "",
        ).strip()

        validacao = validar_acesso(matricula)

        autorizado = validacao["autorizado"]
        motivo = validacao["motivo"]
        aluno = validacao["aluno"]

        RegistroAcesso.objects.create(
            aluno=aluno,
            matricula_informada=matricula,
            autorizado=autorizado,
            motivo=motivo,
        )

        resultado = autorizado

    contexto = {
        "resultado": resultado,
        "motivo": motivo,
        "matricula": matricula,
    }

    return render(
        request,
        "alunos/catraca.html",
        contexto,
    )


# ============================================================
# HISTÓRICO DE ACESSOS
# ============================================================

@exigir_acesso_operacional
def historico_acessos(request):
    registros = (
        RegistroAcesso.objects
        .select_related("aluno")
        .all()
    )

    matricula = request.GET.get(
        "matricula",
        "",
    ).strip()

    resultado = request.GET.get(
        "resultado",
        "todos",
    )

    inicio = request.GET.get("inicio", "")
    fim = request.GET.get("fim", "")

    if matricula:
        registros = registros.filter(
            matricula_informada__icontains=matricula,
        )

    if resultado == "liberado":
        registros = registros.filter(
            autorizado=True,
        )

    elif resultado == "bloqueado":
        registros = registros.filter(
            autorizado=False,
        )

    data_inicio = parse_date(inicio)
    data_fim = parse_date(fim)

    if data_inicio:
        registros = registros.filter(
            data_hora__date__gte=data_inicio,
        )

    if data_fim:
        registros = registros.filter(
            data_hora__date__lte=data_fim,
        )

    contexto = {
        "registros": registros[:200],
        "matricula": matricula,
        "resultado": resultado,
        "inicio": inicio,
        "fim": fim,
    }

    return render(
        request,
        "alunos/historico_acessos.html",
        contexto,
    )


# ============================================================
# PAGAMENTOS E RENOVAÇÃO DE MENSALIDADES
# ============================================================

@exigir_acesso_operacional
def pagamentos(request):
    if request.method == "POST":
        form = PagamentoForm(request.POST)

        if form.is_valid():
            pagamento = form.save(commit=False)
            hoje = timezone.localdate()

            with transaction.atomic():
                aluno = (
                    Aluno.objects
                    .select_for_update()
                    .select_related("plano")
                    .get(pk=pagamento.aluno_id)
                )

                mensalidade, criada = (
                    Mensalidade.objects.get_or_create(
                        aluno=aluno,
                        competencia=pagamento.competencia,
                        defaults={
                            "valor_devido": aluno.plano.valor,
                        },
                    )
                )

                pagamento.aluno = aluno
                pagamento.save()

                total_pago = (
                    Pagamento.objects
                    .filter(
                        aluno=aluno,
                        competencia=pagamento.competencia,
                    )
                    .aggregate(
                        total=models.Sum("valor"),
                    )["total"]
                    or 0
                )

                if (
                    total_pago >= mensalidade.valor_devido
                    and not mensalidade.renovacao_aplicada
                ):
                    data_base = max(
                        aluno.validade,
                        hoje,
                    )

                    aluno.validade = (
                        data_base
                        + timedelta(
                            days=aluno.plano.duracao_dias,
                        )
                    )

                    aluno.save(
                        update_fields=["validade"],
                    )

                    mensalidade.renovacao_aplicada = True
                    mensalidade.data_renovacao = hoje

                    mensalidade.save(
                        update_fields=[
                            "renovacao_aplicada",
                            "data_renovacao",
                        ],
                    )

            return redirect("pagamentos")

    else:
        form = PagamentoForm()

    registros = (
        Pagamento.objects
        .select_related("aluno")
        .all()
    )

    matricula = request.GET.get(
        "matricula",
        "",
    ).strip()

    competencia = request.GET.get(
        "competencia",
        "",
    ).strip()

    if matricula:
        registros = registros.filter(
            aluno__matricula__icontains=matricula,
        )

    if competencia:
        registros = registros.filter(
            competencia=competencia,
        )

    contexto = {
        "form": form,
        "registros": registros[:200],
        "matricula": matricula,
        "competencia": competencia,
    }

    return render(
        request,
        "alunos/pagamentos.html",
        contexto,
    )