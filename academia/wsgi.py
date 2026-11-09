"""
Configuração WSGI do projeto academia.

Expõe a aplicação WSGI por meio da variável
de módulo chamada application.

Documentação:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


# Define o módulo de configurações do Django.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "academia.settings",
)

# Inicializa a aplicação WSGI.
application = get_wsgi_application()