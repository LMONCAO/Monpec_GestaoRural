from django.apps import AppConfig
from django.db.models.signals import post_migrate


class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
    
    def ready(self):
        """Executado quando a aplicação está pronta"""
        # Conectar função de criação de admin ao sinal post_migrate
        post_migrate.connect(self.create_admin_user, sender=self)

        # Executar migrações pendentes na inicialização
        self.run_pending_migrations()

            # Importar aqui para evitar importações circulares
        try:
            from django.db import transaction
            from .models import CategoriaAnimal
            # Garantir que todos os modelos especializados sejam registrados
            from . import models_reproducao  # noqa: F401
            from . import models_compras_financeiro  # noqa: F401
            from . import models_iatf_completo  # noqa: F401
            # Importar models_cadastros para garantir que Cliente seja carregado
            from . import models_cadastros  # noqa: F401
            # Importar models_financeiro e models_operacional para garantir que CentroCusto, PlanoConta e Equipamento sejam registrados
            from . import models_financeiro  # noqa: F401
            from . import models_operacional  # noqa: F401
            from . import models_auditoria  # noqa: F401 - Importar para registrar modelos de auditoria
            from .services.provisionamento import registrar_workspaces_existentes
            
            # Criar categorias padrão se não existirem
            self.criar_categorias_padrao()
            registrar_workspaces_existentes()
        except Exception as e:
            # Em caso de erro (por exemplo, durante migrações), apenas logar
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'Erro ao criar categorias padrão na inicialização: {e}')
    
    def criar_categorias_padrao(self):
        """Cria as categorias padrão do sistema se não existirem"""
        from django.db import transaction
        from .models import CategoriaAnimal
        
        categorias_padrao = [
            # FÊMEAS (5 categorias)
            {
                'nome': 'Bezerro(a) 0-12 F',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 0 a 12 Meses'
            },
            {
                'nome': 'Novilha 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 12 a 24 Meses'
            },
            {
                'nome': 'Primíparas 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas Primíparas de 24 a 36 Meses'
            },
            {
                'nome': 'Vacas Descarte +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas de Descarte acima de 36 Meses'
            },
            {
                'nome': 'Vacas em Reprodução +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas em Reprodução acima de 36 Meses'
            },
            
            # MACHOS (4 categorias) - APENAS "Garrote 12-24 M" (não criar "Garrote 12-4 M")
            {
                'nome': 'Bezerro(o) 0-12 M',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Machos de 0 a 12 Meses'
            },
            {
                'nome': 'Garrote 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Garrotes de 12 a 24 Meses'
            },
            {
                'nome': 'Boi 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Bois de 24 a 36 Meses'
            },
            {
                'nome': 'Touro +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Touros acima de 36 Meses'
            },
        ]
        
        try:
            with transaction.atomic():
                for cat_data in categorias_padrao:
                    CategoriaAnimal.objects.get_or_create(
                        nome=cat_data['nome'],
                        defaults={
                            'idade_minima_meses': cat_data.get('idade_minima_meses'),
                            'idade_maxima_meses': cat_data.get('idade_maxima_meses'),
                            'sexo': cat_data.get('sexo', 'I'),
                            'raca': cat_data.get('raca', 'NELORE'),
                            'descricao': cat_data.get('descricao', ''),
                            'ativo': True
                        }
                    )
        except Exception:
            # Se der erro (tabela não existe ainda, por exemplo), ignorar
            pass

    def run_pending_migrations(self):
        """Executar migrações pendentes na inicialização"""
        try:
            from django.core.management import execute_from_command_line
            from django.db import connection
            import sys

            # Verificar se estamos em produção
            import os
            if os.getenv('K_SERVICE') or os.getenv('GAE_ENV'):
                print("🔄 Executando migrações pendentes...")

                # Executar migrações silenciosamente
                old_argv = sys.argv
                try:
                    sys.argv = ['manage.py', 'migrate', '--verbosity=0']
                    execute_from_command_line(sys.argv)
                    print("✅ Migrações executadas com sucesso!")
                except Exception as e:
                    print(f"⚠️ Erro nas migrações: {e}")
                finally:
                    sys.argv = old_argv

        except Exception as e:
            print(f"Erro ao executar migrações: {e}")

    def create_admin_user(self, **kwargs):
        """Cria usuário admin se não existir"""
        try:
            from django.contrib.auth.models import User

            # Só criar se não existir nenhum superusuário
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@monpec.com.br',
                    password='L6171r12@@jjms',
                    first_name='Administrador',
                    last_name='Sistema'
                )
                print('🎉 Superusuário admin criado automaticamente!')
                print('👤 Usuário: admin')
                print('📧 Email: admin@monpec.com.br')
                print('🔑 Senha: L6171r12@@jjms')
            else:
                # Mostrar TODOS os usuários existentes
                print('=== TODOS OS USUÁRIOS EXISTENTES ===')
                all_users = User.objects.all()
                for user in all_users:
                    print(f'• ID: {user.id} | Username: {user.username} | Email: {user.email} | Superuser: {user.is_superuser} | Staff: {user.is_staff}')
                print('=== FIM DA LISTA ===')
        except Exception as e:
            print(f'Erro ao criar/verificar superusuário: {e}')

