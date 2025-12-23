from django.shortcuts import redirect

# -------------------------------------------------------------
# LISTA DE EXCEÇÕES (EXEMPT)
# -------------------------------------------------------------
# Define as URLs que estão isentas (liberadas) da checagem obrigatória do MFA.
# É crucial que as rotas de LOGIN, SETUP, VERIFY e LOGOUT estejam aqui,
# pois o usuário precisa acessar estas telas ANTES de ter o MFA validado na sessão.
EXEMPT = [
    "/accounts/login/",      # Permite o login com senha.
    "/accounts/mfa-setup/",  # Permite configurar o MFA (gerar QR code).
    "/accounts/mfa-verify/", # Permite digitar o código MFA (o objetivo final do fluxo).
    "/accounts/mfa-reset/",  # (Adicionado recentemente) Permite resetar o token perdido.
    "/accounts/logout/",     # Permite sair do sistema.
]

# -------------------------------------------------------------
# MIDDLEWARE: ASSEGURA QUE O MFA FOI CONCLUÍDO
# -------------------------------------------------------------
class EnsureMFAPassedMiddleware:
    # Método construtor obrigatório para Middlewares de classe no Django.
    # get_response é uma função que irá processar a requisição e retornar a resposta.
    def __init__(self, get_response):
        self.get_response = get_response

    # Método que é chamado a cada requisição HTTP que chega ao servidor.
    def __call__(self, request):

        # Obtém o caminho (path) da URL solicitada (ex: "/home/", "/admin/").
        path = request.path

        # 1. CHECAGEM DE EXCEÇÃO: Verifica se a URL solicitada é uma das URLs liberadas (EXEMPT).
        # A função 'any' retorna True se qualquer item em EXEMPT for o início do 'path'.
        if any(path.startswith(e) for e in EXEMPT):
            # Se a URL for liberada, o fluxo normal é mantido.
            return self.get_response(request)

        # 2. CHECAGEM DE AUTENTICAÇÃO: Verifica se o usuário já fez login com e-mail/senha.
        user = request.user

        if user.is_authenticated:
            # 3. CHECAGEM DE MFA: O usuário fez login, mas precisa checar se o MFA foi validado.
            # Verifica se a flag "mfa_passed" NÃO está True na sessão.
            # O valor padrão é False se a chave não existir.
            if not request.session.get("mfa_passed", False):
                # Se o usuário está autenticado mas NÃO passou pelo MFA nesta sessão,
                # ele é forçado a voltar para a tela de verificação MFA.
                # Isso impede que o usuário acesse rotas protegidas (como a /home/).
                return redirect("accounts:mfa_verify")

        # Se o usuário não estiver logado (e não for rota isenta),
        # ou se estiver logado E o MFA tiver sido passado,
        # a requisição segue para a próxima etapa (próxima middleware ou view final).
        return self.get_response(request)