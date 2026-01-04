"""
Management command para garantir que o usuário admin existe com a senha correta.
Execute: python manage.py garantir_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Garante que o usuário admin existe com a senha configurada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--senha',
            type=str,
            default=None,
            help='Senha para o usuário admin (padrão: L6171r12@@ ou variável ADMIN_PASSWORD)',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username do admin (padrão: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@monpec.com.br',
            help='Email do admin (padrão: admin@monpec.com.br)',
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força a atualização da senha mesmo se o usuário já existir',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        senha = options['senha'] or os.getenv('ADMIN_PASSWORD', 'L6171r12@@')
        forcar = options['forcar']

        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('GARANTINDO USUÁRIO ADMIN'))
        self.stdout.write('=' * 60)
        self.stdout.write('')

        try:
            # Buscar ou criar usuário
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuário "{username}" CRIADO')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuário "{username}" ENCONTRADO')
                )
                # Atualizar informações se necessário
                atualizado = False
                if user.email != email:
                    user.email = email
                    atualizado = True
                if not user.is_staff:
                    user.is_staff = True
                    atualizado = True
                if not user.is_superuser:
                    user.is_superuser = True
                    atualizado = True
                if not user.is_active:
                    user.is_active = True
                    atualizado = True
                if atualizado:
                    user.save()
                    self.stdout.write(
                        self.style.WARNING('⚠️ Informações do usuário atualizadas')
                    )

            # Exibir informações do usuário
            self.stdout.write(f'   - Username: {user.username}')
            self.stdout.write(f'   - Email: {user.email}')
            self.stdout.write(f'   - Ativo: {user.is_active}')
            self.stdout.write(f'   - Staff: {user.is_staff}')
            self.stdout.write(f'   - Superuser: {user.is_superuser}')
            self.stdout.write('')

            # Definir/atualizar senha
            if forcar or created:
                self.stdout.write('Definindo senha...')
                user.set_password(senha)
                user.save()
                self.stdout.write(self.style.SUCCESS('✅ Senha definida!'))
            else:
                # Verificar se a senha atual está correta
                self.stdout.write('Verificando senha atual...')
                if user.check_password(senha):
                    self.stdout.write(
                        self.style.SUCCESS('✅ Senha já está correta!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Senha atual não corresponde. Atualizando...')
                    )
                    user.set_password(senha)
                    user.save()
                    self.stdout.write(self.style.SUCCESS('✅ Senha atualizada!'))

            # Testar autenticação
            self.stdout.write('')
            self.stdout.write('Testando autenticação...')
            user_auth = authenticate(username=username, password=senha)
            if user_auth:
                self.stdout.write(
                    self.style.SUCCESS('✅ Autenticação bem-sucedida!')
                )
                self.stdout.write(f'   - ID: {user_auth.id}')
                self.stdout.write(f'   - Username: {user_auth.username}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Autenticação falhou!')
                )
                self.stdout.write(
                    self.style.WARNING(
                        '   Isso pode indicar um problema com o algoritmo de hash.'
                    )
                )
                return

            self.stdout.write('')
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS('✅ SUCESSO!'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Senha: {"*" * len(senha)}')
            self.stdout.write('')
            self.stdout.write('O usuário admin está pronto para uso!')

            # Log para produção
            logger.info(
                f'Admin garantido: username={username}, email={email}, '
                f'created={created}, auth_test=success'
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ ERRO: {e}'))
            logger.error(f'Erro ao garantir admin: {e}', exc_info=True)
            raise





