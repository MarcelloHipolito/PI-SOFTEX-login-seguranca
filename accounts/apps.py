from django.apps import AppConfig

# Define a classe de configuração para o aplicativo 'accounts'.
class AccountsConfig(AppConfig):
    
    # Define o campo de chave primária automática a ser usado para modelos sem PK explícita.
    # BigAutoField é o padrão e recomendado para chaves primárias inteiras grandes.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Define o nome do aplicativo (deve corresponder ao nome do diretório do app).
    name = 'accounts'

    # O método 'ready' é chamado pelo Django quando o aplicativo é inicializado.
    # Este é o lugar correto para carregar códigos que precisam ser executados
    # quando o Django inicia, como o registro de Sinais.
    def ready(self):
        # Importa o módulo signals do próprio aplicativo 'accounts'.
        # Isso garante que as funções receptoras de sinais (como create_user_profile)
        # sejam registradas no sistema de Sinais do Django, ativando a criação
        # automática do UserProfile após a criação de um novo User.
        import accounts.signals