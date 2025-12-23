from django.db import models
from django.contrib.auth.models import User

# Define o modelo (tabela no banco de dados) que estende
# o usuário padrão do Django com informações específicas do projeto.
class UserProfile(models.Model):
    
    # Define um relacionamento um-para-um (OneToOneField) com o modelo User padrão do Django.
    # Quando o User é deletado (CASCADE), o UserProfile associado também é deletado.
    # related_name='profile' permite acessar o perfil a partir do objeto User (ex: user.profile).
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    
    # Campo para armazenar o segredo TOTP (Time-based One-Time Password) usado no MFA.
    # max_length=32 é o tamanho padrão de uma chave base32.
    # blank=True e null=True permitem que o campo comece vazio (antes da configuração do MFA).
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    
    # Booleano que indica se o usuário concluiu a configuração e ativou o MFA.
    # default=False: O MFA é desativado por padrão para novos usuários.
    mfa_enabled = models.BooleanField(default=False)

    # Campos específicos do projeto de Mamografia (informações do profissional)
    institution = models.CharField(max_length=255, blank=True)
    professional_registry = models.CharField(max_length=255, blank=True)

    # Método que define a representação em string do objeto (útil no Django Admin).
    def __str__(self):
        return self.user.username # Retorna o username do usuário associado.