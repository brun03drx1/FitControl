FitControl

Sistema de gerenciamento de academia desenvolvido com Python e Django.

O FitControl é uma aplicação web desenvolvida para auxiliar no gerenciamento das atividades de uma academia, reunindo em um único sistema o controle de alunos, planos, pagamentos, mensalidades e registros de acesso.

O projeto tem como finalidade aplicar conhecimentos de desenvolvimento web, organização de aplicações, modelagem de dados, autenticação e implementação de regras de negócio.

⸻

Tecnologias

⸻

Funcionalidades

Módulo	Descrição
Alunos	Cadastro, consulta, edição e gerenciamento de alunos.
Planos	Cadastro e gerenciamento dos planos da academia.
Pagamentos	Registro e acompanhamento dos pagamentos.
Mensalidades	Controle de competências e renovações.
Catraca	Simulação e validação de acesso dos alunos.
Histórico	Registro de tentativas de acesso autorizadas e bloqueadas.
Usuários	Autenticação e controle de permissões.
Painel	Visualização de informações operacionais.

Recursos adicionais

* Renovação de matrícula condicionada à quitação integral do plano na competência.
* Validação da situação e da validade da matrícula.
* Registro automático das tentativas de acesso.
* Interface personalizada com tema escuro.
* Organização de funcionalidades por permissões de usuário.

⸻

Interface

O sistema utiliza uma interface com tema escuro, elementos em azul e organização visual voltada à facilidade de navegação.

⸻

Estrutura do projeto

academia/
│
├── academia/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── alunos/
│   ├── migrations/
│   ├── static/
│   │   └── alunos/css/
│   ├── templates/
│   │   └── alunos/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissoes.py
│   ├── servicos_acesso.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore
├── manage.py
└── README.md

⸻

Instalação

Pré-requisitos

* Python 3.13 ou superior compatível.
* pip.
* Git.

1. Clonar o repositório

git clone URL_DO_REPOSITORIO

2. Acessar o diretório

cd academia

3. Criar o ambiente virtual

python -m venv .venv

4. Ativar o ambiente virtual

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

5. Instalar as dependências

pip install -r requirements.txt

6. Configurar a chave secreta

No Windows PowerShell:

$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

7. Executar as migrações

python manage.py migrate

8. Criar usuário administrador

python manage.py createsuperuser

9. Iniciar o servidor

python manage.py runserver

A aplicação estará disponível em:

Sistema: http://127.0.0.1:8000/

Administração: http://127.0.0.1:8000/admin/

⸻

Segurança e ambiente

* A chave secreta é configurada por variável de ambiente.
* Bancos de dados locais e arquivos temporários são excluídos do versionamento.
* O projeto utiliza autenticação e permissões para restringir funcionalidades.

⸻

Status do projeto

Em desenvolvimento.

O FitControl é uma versão destinada a estudos, aprimoramento técnico e apresentação de portfólio. A funcionalidade de catraca é simulada, sem integração com equipamentos físicos.

⸻

Autor

Bruno Eduardo Rodrigues Xavier

⸻

Desenvolvido como projeto prático de estudos em Python e desenvolvimento web.