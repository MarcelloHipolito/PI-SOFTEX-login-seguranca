📄 README — Projeto Django com MFA (TOTP)

Este documento apresenta a estrutura, dependências, comandos essenciais e o funcionamento do sistema de Autenticação de Múltiplos Fatores (MFA) baseado em TOTP (Time-based One-Time Password) implementado no projeto Django.

1. ⚙️ Pré-requisitos e Dependências

Para executar o projeto, você precisa:

Python 3.8+

pip instalado

As dependências estão listadas no arquivo requirements.txt.

🧩 Dependências Principais
Dependência	Versão	Finalidade
Django	4.2	Framework principal
pyotp	Qualquer	Geração e verificação de códigos TOTP
qrcode[pil]	Qualquer	Geração de QR Code
Pillow	Qualquer	Biblioteca para manipulação de imagens
📥 Instalação

No diretório raiz do projeto, execute:

pip install -r requirements.txt

2. 🚀 Inicialização do Projeto

Siga esta sequência de comandos no terminal para configurar e rodar o sistema.

1️⃣ Criar e Aplicar Migrações

Cria as tabelas do UserProfile e demais estruturas necessárias:

# 1. Cria o arquivo de migrações para o app "accounts"
python manage.py makemigrations accounts

# 2. Aplica todas as migrações
python manage.py migrate

2️⃣ Criar Usuário Inicial

Crie um usuário administrador:

python manage.py createsuperuser

3️⃣ Rodar o Servidor
python manage.py runserver


O sistema estará disponível em:

http://127.0.0.1:8000/

Tela de login: /accounts/login/

3. 🛡️ Fluxo do MFA (Segurança)

O fluxo de autenticação e MFA é controlado por Views e Middleware.

🔐 A. Fluxo de Login (views.py)
Rota	View	Função

```
/accounts/login/	login_view	Etapa 1: valida e-mail e senha. Salva pre_mfa_user_id na sessão.
/accounts/mfa-setup/	mfa_setup_view	Etapa 2: geração do totp_secret, salva no banco e exibe o QR Code.
/accounts/mfa-verify/	mfa_verify_view	Etapa 3: recebe o código TOTP, valida com pyotp.TOTP(secret).verify(), e define mfa_passed=True.
/accounts/mfa-reset/	mfa_reset_view	Reseta o MFA do usuário (zera o totp_secret).
/accounts/logout/	logout_view	Faz logout e limpa a sessão (inclusive mfa_passed).
```
🛡️ B. Middleware de Segurança (middleware.py)

A classe EnsureMFAPassedMiddleware garante:

Executa em todas as requisições (exceto rotas isentas).

Verifica:

Se o usuário está autenticado.

Se a sessão contém mfa_passed=True.

Se não tiver MFA validado, redireciona para /accounts/mfa-verify/.

Isso impede totalmente o acesso a páginas protegidas apenas com senha — o MFA é obrigatório.

4. 📂 Estrutura de Arquivos
Arquivo	Local	Função
models.py	accounts/	Define UserProfile com totp_secret e mfa_enabled.
signals.py	accounts/	Cria automaticamente um UserProfile ao criar um User.
apps.py	accounts/	Carrega os signals na inicialização do Django.
urls.py	accounts/	Mapeia as rotas: login, setup, verify, reset, logout.

---

### Desenvolvido por:
**Marcello Henrique**
