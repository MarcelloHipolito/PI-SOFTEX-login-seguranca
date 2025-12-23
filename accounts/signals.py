from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# Importa o sinal 'post_save', que é emitido após um objeto ser salvo no banco de dados.
# Importa 'receiver', um decorador que registra uma função como um receptor de sinal.
# Importa o modelo User padrão do Django e o modelo UserProfile personalizado.

# -------------------------------------------------------------
# RECEPTOR DE SINAL PARA CRIAÇÃO DE PERFIL
# -------------------------------------------------------------

# O decorador @receiver registra a função 'create_user_profile' para ser executada:
# 1. Quando o sinal 'post_save' (depois de salvar) for enviado.
# 2. Pelo modelo 'User' (sender=User), ou seja, sempre que um objeto User for salvo.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # 'instance' é o objeto User que acabou de ser salvo.
    # 'created' é um booleano que é True se o objeto acabou de ser criado (pela primeira vez).
    
    # Verifica se o objeto User foi recém-criado no banco de dados.
    # Isso evita que o UserProfile seja criado novamente toda vez que o User for atualizado.
    if created:
        # Cria um novo objeto UserProfile e o associa ao objeto User recém-criado (instance).
        # Isso garante que todo novo usuário tenha um perfil para armazenar o segredo MFA.
        UserProfile.objects.create(user=instance)