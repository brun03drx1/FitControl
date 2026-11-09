from django import forms

from .models import Aluno, Pagamento


# ============================================================
# FORMULÁRIO DE CADASTRO E EDIÇÃO DE ALUNOS
# ============================================================

class AlunoForm(forms.ModelForm):
    """Formulário para cadastrar e editar alunos."""

    class Meta:
        model = Aluno

        fields = [
            "matricula",
            "nome",
            "telefone",
            "validade",
            "ativo",
            "plano",
        ]

        widgets = {
            "validade": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["validade"].input_formats = [
            "%Y-%m-%d",
        ]


# ============================================================
# FORMULÁRIO DE REGISTRO DE PAGAMENTOS
# ============================================================

class PagamentoForm(forms.ModelForm):
    """Formulário para registrar pagamentos de mensalidades."""

    class Meta:
        model = Pagamento

        fields = [
            "aluno",
            "valor",
            "data_pagamento",
            "competencia",
            "forma_pagamento",
            "observacao",
        ]

        widgets = {
            "data_pagamento": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),

            "competencia": forms.TextInput(
                attrs={
                    "type": "month",
                    "placeholder": "AAAA-MM",
                },
            ),

            "observacao": forms.TextInput(
                attrs={
                    "maxlength": 200,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["data_pagamento"].input_formats = [
            "%Y-%m-%d",
        ]

    # --------------------------------------------------------
    # VALIDAÇÃO DO VALOR
    # --------------------------------------------------------

    def clean_valor(self):
        valor = self.cleaned_data["valor"]

        if valor <= 0:
            raise forms.ValidationError(
                "O valor do pagamento deve ser maior que zero."
            )

        return valor

    # --------------------------------------------------------
    # VALIDAÇÃO DA COMPETÊNCIA
    # --------------------------------------------------------

    def clean_competencia(self):
        competencia = self.cleaned_data["competencia"]

        try:
            ano_texto, mes_texto = competencia.split("-")

            ano = int(ano_texto)
            mes = int(mes_texto)

        except (ValueError, AttributeError):
            raise forms.ValidationError(
                "Informe a competência no formato AAAA-MM."
            )

        if ano < 2000 or not 1 <= mes <= 12:
            raise forms.ValidationError(
                "Informe um mês e ano válidos."
            )

        return competencia

    # --------------------------------------------------------
    # VALIDAÇÃO DO ALUNO E DO PLANO
    # --------------------------------------------------------

    def clean_aluno(self):
        aluno = self.cleaned_data["aluno"]

        if not aluno.plano:
            raise forms.ValidationError(
                "Associe um plano ao aluno antes de registrar "
                "o pagamento."
            )

        if not aluno.plano.ativo:
            raise forms.ValidationError(
                "O plano do aluno está inativo. "
                "Selecione um plano ativo."
            )

        return aluno