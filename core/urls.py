"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Arquivo: core/urls.py (O principal do seu projeto)

from django.contrib import admin
from django.urls import path, include

# -------------------------------------------------------------
# ➡️ IMPORTANTE: Importe a home_view do arquivo core/views.py
# O ponto ( . ) significa "deste pacote/diretório", que é o 'core'.
from .views import home_view 
# -------------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas do seu app accounts (login, mfa, logout)
    path('accounts/', include('accounts.urls')),
    
    # -------------------------------------------------------------
    # ➡️ NOVA ROTA: Define a página inicial
    path('', home_view, name='home'), # Esta linha mapeia a URL '/' para a home_view e dá o nome 'home'
    # -------------------------------------------------------------
]

