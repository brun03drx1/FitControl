"""
Configuração ASGI do projeto academia.

Expõe a aplicação ASGI por meio da variável
de módulo chamada application.

Documentação:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


# Define o módulo de configurações do Django.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "academia.settings",
)

# Inicializa a aplicação ASGI.
application = get_asgi_application()
