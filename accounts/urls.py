from django.urls import path
from . import views

# Importa a função 'path' para definir rotas de URL.
# Importa 'views' do diretório atual (o 'accounts' app) para mapear as URLs às funções.

# Define o namespace do aplicativo. Isso permite referenciar URLs como 'accounts:login'.
app_name = "accounts"

# Lista de padrões de URL (URLs Patterns) que o Django usará para rotear as requisições.
urlpatterns = [
    # Rota para a tela de login (e-mail e senha).
    # Chama a função views.login_view. Nomeada como 'login'.
    path("login/", views.login_view, name="login"),
    
    # Rota para a tela de configuração do MFA (exibe o QR Code).
    # Chama a função views.mfa_setup_view. Nomeada como 'mfa_setup'.
    path("mfa-setup/", views.mfa_setup_view, name="mfa_setup"),
    
    # Rota para a tela de verificação do MFA (recebe o código de 6 dígitos).
    # Chama a função views.mfa_verify_view. Nomeada como 'mfa_verify'.
    path("mfa-verify/", views.mfa_verify_view, name="mfa_verify"),
    
    # Rota para o processo de logout.
    # Chama a função views.logout_view. Nomeada como 'logout'.
    path("logout/", views.logout_view, name="logout"),
    
    # Rota de emergência para resetar o segredo MFA.
    # Usada quando o usuário perde o acesso ao aplicativo autenticador.
    # Chama a função views.mfa_reset_view. Nomeada como 'mfa_reset'.
    path("mfa-reset/", views.mfa_reset_view, name="mfa_reset"),
]