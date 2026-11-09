from django.db import models
from django.utils import timezone


# ============================================================
# MODELO DE PLANOS
# ============================================================

class Plano(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
    )

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    duracao_dias = models.PositiveIntegerField(
        default=30,
    )

    ativo = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"

    class Meta:
        ordering = ["nome"]
        verbose_name = "Plano"
        verbose_name_plural = "Planos"


# ============================================================
# MODELO DE ALUNOS
# ============================================================

class Aluno(models.Model):
    matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Matrícula",
    )

    nome = models.CharField(
        max_length=150,
        verbose_name="Nome completo",
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
    )

    validade = models.DateField(
        verbose_name="Validade da matrícula",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Aluno ativo",
    )

    plano = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Plano contratado",
    )

    def __str__(self):
        return f"{self.matricula} - {self.nome}"

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ["nome"]


# ============================================================
# MODELO DE REGISTROS DE ACESSO
# ============================================================

class RegistroAcesso(models.Model):
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Aluno",
    )

    matricula_informada = models.CharField(
        max_length=20,
    )

    autorizado = models.BooleanField(
        default=False,
    )

    motivo = models.CharField(
        max_length=200,
    )

    data_hora = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        resultado = (
            "Liberado" if self.autorizado else "Bloqueado"
        )
        return f"{self.matricula_informada} - {resultado}"

    class Meta:
        verbose_name = "Registro de acesso"
        verbose_name_plural = "Registros de acesso"
        ordering = ["-data_hora"]


# ============================================================
# MODELO DE PAGAMENTOS
# ============================================================

class Pagamento(models.Model):
    FORMAS_PAGAMENTO = [
        ("dinheiro", "Dinheiro"),
        ("pix", "PIX"),
        ("cartao_credito", "Cartão de crédito"),
        ("cartao_debito", "Cartão de débito"),
        ("transferencia", "Transferência"),
    ]

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        related_name="pagamentos",
        verbose_name="Aluno",
    )

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Valor pago",
    )

    data_pagamento = models.DateField(
        default=timezone.localdate,
        verbose_name="Data do pagamento",
    )

    competencia = models.CharField(
        max_length=7,
        verbose_name="Referência (AAAA-MM)",
        help_text="Exemplo: 2026-10",
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMAS_PAGAMENTO,
        verbose_name="Forma de pagamento",
    )

    observacao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Observação",
    )

    def __str__(self):
        return f"{self.aluno.nome} - R$ {self.valor}"

    class Meta:
        ordering = ["-data_pagamento"]
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"


# ============================================================
# MODELO DE MENSALIDADES
# ============================================================

class Mensalidade(models.Model):
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        related_name="mensalidades",
        verbose_name="Aluno",
    )

    competencia = models.CharField(
        max_length=7,
        verbose_name="Competência (AAAA-MM)",
    )

    valor_devido = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Valor devido",
    )

    renovacao_aplicada = models.BooleanField(
        default=False,
        verbose_name="Renovação aplicada",
    )

    data_renovacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da renovação",
    )

    class Meta:
        ordering = ["-competencia"]
        verbose_name = "Mensalidade"
        verbose_name_plural = "Mensalidades"

        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "competencia"],
                name="unica_mensalidade_aluno_competencia",
            ),
        ]

    def __str__(self):
        return f"{self.aluno.nome} - {self.competencia}"