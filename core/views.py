# Arquivo: core/views.py (Novo arquivo no diretório do projeto 'core')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# IMPORTANTE: A sua própria EnsureMFAPassedMiddleware já protege esta rota,
# mas o @login_required garante que só usuários autenticados a acessem.

@login_required
def home_view(request):
    # O Django buscará o template em core/templates/core/home.html
    return render(request, "core/home.html")