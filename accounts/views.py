import io
import base64
import pyotp
import qrcode

# Importações básicas do Django para renderizar templates, redirecionar e manipulação de sessão.
from django.shortcuts import render, redirect
# Importações para autenticação (login, logout, verificação de senha).
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Decorator para exigir que o usuário esteja logado (não totalmente necessário neste fluxo, mas boa prática).
from django.contrib.auth.decorators import login_required
# Módulo para enviar mensagens de erro ou sucesso para o template.
from django.contrib import messages
# Modelos de usuário padrão do Django e configurações.
from django.contrib.auth.models import User
from django.conf import settings

# Modelo do perfil de usuário customizado (onde o totp_secret é armazenado).
from .models import UserProfile


# ------------------------------------------
# Função auxiliar para gerar o QR Code
# ------------------------------------------
def generate_qr_code(uri):
    # Cria um objeto QR Code a partir da URI (link com o segredo TOTP).
    qr = qrcode.make(uri)
    # Cria um buffer de memória (IO) para armazenar a imagem temporariamente.
    buffer = io.BytesIO()
    # Salva a imagem do QR Code no buffer como formato PNG.
    qr.save(buffer, format='PNG')
    # Codifica o conteúdo do buffer para Base64. Isso permite incorporar a imagem
    # diretamente no HTML sem precisar salvar um arquivo no disco.
    return base64.b64encode(buffer.getvalue()).decode()


# ------------------------------------------
# LOGIN COM EMAIL + SENHA
# ------------------------------------------
def login_view(request):
    # Lógica executada apenas se o formulário for submetido (POST).
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1. Tenta encontrar o usuário pelo e-mail (usado para encontrar o username).
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Caso o e-mail não exista, exibe uma mensagem de erro.
            messages.error(request, "Email não encontrado.")
            return render(request, "accounts/login.html")

        # 2. Tenta autenticar o usuário com a senha fornecida.
        # Usa o username do usuário encontrado e a senha.
        auth_user = authenticate(
            request, username=user.username, password=password
        )

        # Se a autenticação falhar (senha incorreta).
        if auth_user is None:
            messages.error(request, "Senha incorreta.")
            return render(request, "accounts/login.html")

        # 3. AUTENTICAÇÃO DE SENHA BEM-SUCEDIDA:
        
        # Armazena o ID do usuário na sessão. O login completo (auth_login) AINDA NÃO FOI FEITO.
        # Isso é um estado de "pré-MFA" que o middleware ignora.
        request.session["pre_mfa_user_id"] = auth_user.id

        # 4. Checa o status do MFA.
        
        # Se o usuário NÃO tiver MFA ainda (mfa_enabled=False) → vai para a tela de setup (QR Code).
        if not auth_user.profile.mfa_enabled:
            return redirect("accounts:mfa_setup")

        # Se já tiver MFA ativado → vai para a tela de verificação (código de 6 dígitos).
        return redirect("accounts:mfa_verify")

    # Para requisições GET, apenas renderiza o template de login.
    return render(request, "accounts/login.html")


# ------------------------------------------
# TELA PARA EXIBIR O QR CODE (SETUP INICIAL)
# ------------------------------------------
def mfa_setup_view(request):
    # Recupera o ID do usuário que acabou de passar pelo login de senha.
    user_id = request.session.get("pre_mfa_user_id")
    # Se não houver ID na sessão (usuário não logou), redireciona para o login.
    if not user_id:
        return redirect("accounts:login")

    user = User.objects.get(id=user_id)
    profile = user.profile

    # Geração do Segredo TOTP:
    # Se o perfil ainda não tem um segredo MFA.
    if not profile.totp_secret:
        # Gera uma nova chave secreta usando o pyotp.
        secret = pyotp.random_base32()
        profile.totp_secret = secret
        profile.save() # Salva a chave no banco de dados.
    else:
        # Se já existir, usa a chave existente.
        secret = profile.totp_secret

    # Geração da URI (Uniform Resource Identifier) para o aplicativo autenticador.
    issuer = "SistemaTermografia"
    # O pyotp gera o link completo que contém o segredo, o e-mail e o nome do emissor.
    uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=issuer)

    # Gera o QR Code em formato Base64 para ser incorporado ao template.
    qr_code = generate_qr_code(uri)

    # Renderiza a tela de setup, passando o QR Code e o segredo (para entrada manual).
    return render(request, "accounts/mfa_setup.html", {
        "qr_code": qr_code,
        "secret": secret,
    })


# ------------------------------------------
# TELA DE VERIFICAÇÃO DO MFA
# ------------------------------------------
def mfa_verify_view(request):
    # Checa se o usuário está no estado de pré-MFA.
    user_id = request.session.get("pre_mfa_user_id")
    if not user_id:
        return redirect("accounts:login")

    user = User.objects.get(id=user_id)
    profile = user.profile

    # Checagem de segurança/reset: Se o usuário está aqui mas o segredo sumiu
    # (Ex: perdeu o celular e usou o reset), redireciona para o setup.
    if not profile.totp_secret:
        return redirect("accounts:mfa_setup")

    # Lógica de verificação do código (POST).
    if request.method == "POST":
        code = request.POST.get("code")  # Recebe o código digitado.
        
        # Cria um objeto TOTP usando o segredo do usuário.
        totp = pyotp.TOTP(profile.totp_secret)

        # Verifica se o código é válido. valid_window=1 permite verificar
        # o código atual e o anterior, dando 30 segundos de margem.
        if totp.verify(code, valid_window=1):
            # 1. Login definitivo do Django:
            auth_login(request, user)

            # 2. Definição da flag de sucesso do MFA na sessão (crucial para o middleware):
            request.session["mfa_passed"] = True
            request.session["user_id"] = user.id
            # Define o tempo de expiração da sessão.
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            # 3. Atualiza o perfil: MFA é oficialmente ativado.
            profile.mfa_enabled = True
            profile.save()

            # 4. Limpa o ID de pré-MFA da sessão.
            del request.session["pre_mfa_user_id"]

            # 5. Redireciona para a página inicial protegida.
            return redirect("home")

        # Se o código for inválido.
        messages.error(request, "Código incorreto. Tente novamente.")

    # Renderiza a tela de verificação (GET).
    return render(request, "accounts/mfa_verify.html")


# ------------------------------------------
# TELA DE RESET DE MFA
# ------------------------------------------
def mfa_reset_view(request):
    """
    Limpa o segredo MFA do usuário atualmente tentando se autenticar (pre_mfa_user_id).
    Esta é a rota de emergência.
    """
    # 1. Checa se o usuário está no estado de pré-MFA.
    user_id = request.session.get("pre_mfa_user_id")
    if not user_id:
        return redirect("accounts:login")

    # 2. Lógica de reset (POST):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Reseta o MFA no banco de dados, limpando o segredo e desativando o flag.
        profile.totp_secret = None
        profile.mfa_enabled = False
        profile.save()
        
        messages.success(request, "Seu código MFA foi resetado. Configure um novo token.")
        
        # Redireciona para o Setup para que um novo QR code seja gerado imediatamente.
        return redirect("accounts:mfa_setup")

    # Se a requisição for GET, exibe a tela de confirmação de reset.
    return render(request, "accounts/mfa_reset_confirm.html")


# ------------------------------------------
# LOGOUT
# ------------------------------------------
# O decorador exige que o usuário esteja logado para acessar esta função.
@login_required
def logout_view(request):
    # Desloga o usuário do Django.
    auth_logout(request)
    # Limpa todos os dados da sessão, incluindo a flag "mfa_passed".
    request.session.flush()
    # Redireciona para a tela de login.
    return redirect("accounts:login")