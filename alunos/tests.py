from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Aluno,
    Mensalidade,
    Pagamento,
    Plano,
    RegistroAcesso,
)
from .servicos_acesso import validar_acesso


# ============================================================
# TESTES DOS MODELOS DO FITCONTROL
# ============================================================

class ModelosFitControlTest(TestCase):
    """Testa a criação e os dados básicos dos modelos."""

    def setUp(self):
        self.plano = Plano.objects.create(
            nome="Plano Teste",
            valor=Decimal("100.00"),
            duracao_dias=30,
            ativo=True,
        )

        self.aluno = Aluno.objects.create(
            matricula="TESTE001",
            nome="Aluno de Teste",
            telefone="31999999999",
            validade=date(2027, 12, 31),
            ativo=True,
            plano=self.plano,
        )

    def test_criar_plano(self):
        self.assertEqual(self.plano.nome, "Plano Teste")
        self.assertEqual(self.plano.valor, Decimal("100.00"))
        self.assertTrue(self.plano.ativo)

    def test_criar_aluno(self):
        self.assertEqual(self.aluno.matricula, "TESTE001")
        self.assertEqual(self.aluno.plano, self.plano)
        self.assertTrue(self.aluno.ativo)

    def test_registro_de_acesso_bloqueado(self):
        registro = RegistroAcesso.objects.create(
            aluno=self.aluno,
            matricula_informada=self.aluno.matricula,
            autorizado=False,
            motivo="Teste de acesso bloqueado",
        )

        self.assertFalse(registro.autorizado)
        self.assertEqual(registro.aluno, self.aluno)
        self.assertEqual(
            registro.motivo,
            "Teste de acesso bloqueado",
        )

    def test_criar_pagamento(self):
        pagamento = Pagamento.objects.create(
            aluno=self.aluno,
            valor=Decimal("100.00"),
            competencia="2027-12",
            forma_pagamento="pix",
        )

        self.assertEqual(
            Decimal(str(pagamento.valor)),
            Decimal("100.00"),
        )
        self.assertEqual(pagamento.competencia, "2027-12")
        self.assertEqual(pagamento.forma_pagamento, "pix")

    def test_criar_mensalidade(self):
        mensalidade = Mensalidade.objects.create(
            aluno=self.aluno,
            competencia="2027-12",
            valor_devido=Decimal("100.00"),
        )

        self.assertEqual(mensalidade.aluno, self.aluno)
        self.assertEqual(
            mensalidade.valor_devido,
            Decimal("100.00"),
        )
        self.assertFalse(mensalidade.renovacao_aplicada)


# ============================================================
# TESTES DE VALIDAÇÃO DA CATRACA
# ============================================================

class ValidacaoCatracaTest(TestCase):
    """Testa as regras de autorização de entrada."""

    def setUp(self):
        self.plano = Plano.objects.create(
            nome="Plano Catraca",
            valor=Decimal("100.00"),
            duracao_dias=30,
            ativo=True,
        )

    def criar_aluno(self, matricula, ativo=True, validade=None):
        return Aluno.objects.create(
            matricula=matricula,
            nome="Aluno Teste Catraca",
            validade=validade or date(2099, 12, 31),
            ativo=ativo,
            plano=self.plano,
        )

    def test_matricula_valida_e_autorizada(self):
        aluno = self.criar_aluno("CAT001")

        resultado = validar_acesso(aluno.matricula)

        self.assertTrue(resultado["autorizado"])
        self.assertEqual(resultado["aluno"], aluno)

    def test_aluno_inativo_e_bloqueado(self):
        aluno = self.criar_aluno("CAT002", ativo=False)

        resultado = validar_acesso(aluno.matricula)

        self.assertFalse(resultado["autorizado"])
        self.assertEqual(
            resultado["motivo"],
            "Aluno bloqueado ou inativo.",
        )

    def test_matricula_vencida_e_bloqueada(self):
        aluno = self.criar_aluno(
            "CAT003",
            validade=date(2000, 1, 1),
        )

        resultado = validar_acesso(aluno.matricula)

        self.assertFalse(resultado["autorizado"])
        self.assertEqual(
            resultado["motivo"],
            "Matrícula vencida.",
        )

    def test_matricula_inexistente_e_bloqueada(self):
        resultado = validar_acesso("NAOEXISTE")

        self.assertFalse(resultado["autorizado"])
        self.assertIsNone(resultado["aluno"])
        self.assertEqual(
            resultado["motivo"],
            "Aluno não cadastrado.",
        )

    def test_matricula_vazia_e_bloqueada(self):
        resultado = validar_acesso("   ")

        self.assertFalse(resultado["autorizado"])
        self.assertIsNone(resultado["aluno"])
        self.assertEqual(
            resultado["motivo"],
            "Informe a matrícula.",
        )


# ============================================================
# TESTES DE PAGAMENTOS E RENOVAÇÃO
# ============================================================

class PagamentosRenovacaoTest(TestCase):
    """Testa pagamentos parciais e renovação de mensalidades."""

    def setUp(self):
        self.plano = Plano.objects.create(
            nome="Plano Pagamento Teste",
            valor=Decimal("100.00"),
            duracao_dias=30,
            ativo=True,
        )

        self.validade_inicial = (
            timezone.localdate() + timedelta(days=5)
        )

        self.aluno = Aluno.objects.create(
            matricula="PAG001",
            nome="Aluno Pagamento Teste",
            telefone="31999999999",
            validade=self.validade_inicial,
            ativo=True,
            plano=self.plano,
        )

        self.usuario = None

    def criar_usuario_operacional(self):
        from django.contrib.auth.models import Group, User

        grupo, _ = Group.objects.get_or_create(
            name="Funcionarios da Academia"
        )

        usuario = User.objects.create_user(
            username="funcionario_teste",
            password="SenhaTeste123!",
        )
        usuario.groups.add(grupo)

        return usuario

    def registrar_pagamento(self, valor):
        self.client.force_login(self.usuario)

        return self.client.post(
            reverse("pagamentos"),
            {
                "aluno": self.aluno.pk,
                "valor": str(valor),
                "data_pagamento": timezone.localdate().isoformat(),
                "competencia": "2099-12",
                "forma_pagamento": "pix",
                "observacao": "",
            },
        )

    def setUp_operacional(self):
        self.usuario = self.criar_usuario_operacional()

    def test_pagamento_parcial_nao_renova_matricula(self):
        self.setUp_operacional()

        resposta = self.registrar_pagamento(Decimal("40.00"))

        self.assertEqual(resposta.status_code, 302)

        self.aluno.refresh_from_db()

        mensalidade = Mensalidade.objects.get(
            aluno=self.aluno,
            competencia="2099-12",
        )

        self.assertEqual(
            self.aluno.validade,
            self.validade_inicial,
        )
        self.assertFalse(mensalidade.renovacao_aplicada)

    def test_pagamento_completo_renova_matricula(self):
        self.setUp_operacional()

        resposta = self.registrar_pagamento(Decimal("100.00"))

        self.assertEqual(resposta.status_code, 302)

        self.aluno.refresh_from_db()

        mensalidade = Mensalidade.objects.get(
            aluno=self.aluno,
            competencia="2099-12",
        )

        self.assertEqual(
            self.aluno.validade,
            self.validade_inicial + timedelta(days=30),
        )
        self.assertTrue(mensalidade.renovacao_aplicada)
        self.assertEqual(
            mensalidade.data_renovacao,
            timezone.localdate(),
        )

    def test_pagamento_adicional_nao_renova_duas_vezes(self):
        self.setUp_operacional()

        self.registrar_pagamento(Decimal("100.00"))

        self.aluno.refresh_from_db()
        validade_apos_renovacao = self.aluno.validade

        self.registrar_pagamento(Decimal("20.00"))

        self.aluno.refresh_from_db()

        self.assertEqual(
            self.aluno.validade,
            validade_apos_renovacao,
        )

    def test_pagamento_com_valor_zero_e_rejeitado(self):
        self.setUp_operacional()

        resposta = self.registrar_pagamento(Decimal("0.00"))

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Pagamento.objects.filter(aluno=self.aluno).exists()
        )

    def test_pagamento_com_valor_negativo_e_rejeitado(self):
        self.setUp_operacional()

        resposta = self.registrar_pagamento(Decimal("-10.00"))

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Pagamento.objects.filter(aluno=self.aluno).exists()
        )

    def test_competencia_com_mes_invalido_e_rejeitada(self):
        self.setUp_operacional()
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            reverse("pagamentos"),
            {
                "aluno": self.aluno.pk,
                "valor": "50.00",
                "data_pagamento": timezone.localdate().isoformat(),
                "competencia": "2026-13",
                "forma_pagamento": "pix",
                "observacao": "",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Pagamento.objects.filter(aluno=self.aluno).exists()
        )

    def test_competencia_com_formato_invalido_e_rejeitada(self):
        self.setUp_operacional()
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            reverse("pagamentos"),
            {
                "aluno": self.aluno.pk,
                "valor": "50.00",
                "data_pagamento": timezone.localdate().isoformat(),
                "competencia": "2026/10",
                "forma_pagamento": "pix",
                "observacao": "",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Pagamento.objects.filter(aluno=self.aluno).exists()
        )

    def test_pagamento_de_aluno_com_plano_inativo_e_rejeitado(self):
        self.setUp_operacional()

        self.plano.ativo = False
        self.plano.save(update_fields=["ativo"])

        resposta = self.registrar_pagamento(Decimal("50.00"))

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Pagamento.objects.filter(aluno=self.aluno).exists()
        )


# ============================================================
# TESTES DE PERMISSÕES E SEGURANÇA
# ============================================================

class PermissoesFitControlTest(TestCase):
    """Testa o acesso às páginas operacionais."""

    def setUp(self):
        self.grupo, _ = Group.objects.get_or_create(
            name="Funcionarios da Academia"
        )

        self.funcionario = User.objects.create_user(
            username="funcionario_permissao_teste",
            password="SenhaTeste123!",
        )
        self.funcionario.groups.add(self.grupo)

        self.usuario_sem_permissao = User.objects.create_user(
            username="usuario_sem_permissao_teste",
            password="SenhaTeste123!",
        )

        self.superusuario = User.objects.create_superuser(
            username="superusuario_permissao_teste",
            email="superusuario@teste.local",
            password="SenhaTeste123!",
        )

        self.url_painel = reverse("painel_inicial")

    def test_usuario_nao_autenticado_e_redirecionado(self):
        resposta = self.client.get(self.url_painel)

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.url)

    def test_funcionario_autorizado_acessa_painel(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.get(self.url_painel)

        self.assertEqual(resposta.status_code, 200)

    def test_usuario_sem_permissao_nao_acessa_painel(self):
        self.client.force_login(self.usuario_sem_permissao)

        resposta = self.client.get(self.url_painel)

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.url)

    def test_superusuario_acessa_painel(self):
        self.client.force_login(self.superusuario)

        resposta = self.client.get(self.url_painel)

        self.assertEqual(resposta.status_code, 200)

    def test_funcionario_nao_pode_alterar_status_aluno(self):
        plano = Plano.objects.create(
            nome="Plano Permissao",
            valor=Decimal("100.00"),
            duracao_dias=30,
            ativo=True,
        )

        aluno = Aluno.objects.create(
            matricula="PERM001",
            nome="Aluno Teste Permissao",
            telefone="31999999999",
            validade=date(2099, 12, 31),
            ativo=True,
            plano=plano,
        )

        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse(
                "alternar_status_aluno",
                args=[aluno.pk],
            )
        )

        aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(aluno.ativo)

    def test_superusuario_pode_alterar_status_aluno(self):
        plano = Plano.objects.create(
            nome="Plano Superusuario",
            valor=Decimal("100.00"),
            duracao_dias=30,
            ativo=True,
        )

        aluno = Aluno.objects.create(
            matricula="PERM002",
            nome="Aluno Teste Superusuario",
            telefone="31999999999",
            validade=date(2099, 12, 31),
            ativo=True,
            plano=plano,
        )

        self.client.force_login(self.superusuario)

        resposta = self.client.post(
            reverse(
                "alternar_status_aluno",
                args=[aluno.pk],
            )
        )

        aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(aluno.ativo)