"""
Comando Django para verificar e corrigir problemas de segurança
Uso: python manage.py verificar_seguranca
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestao_rural.security import (
    verificar_usuarios_inseguros,
    desabilitar_usuarios_padrao,
    USUARIOS_PADRAO_PERIGOSOS
)


class Command(BaseCommand):
    help = 'Verifica e corrige problemas de segurança no sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corrigir',
            action='store_true',
            help='Corrige automaticamente os problemas encontrados',
        )
        parser.add_argument(
            '--desabilitar-padrao',
            action='store_true',
            help='Desabilita usuários padrão perigosos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n=== VERIFICAÇÃO DE SEGURANÇA DO SISTEMA ===\n'))
        
        # 1. Verifica usuários inseguros
        self.stdout.write(self.style.SUCCESS('1. Verificando usuários inseguros...'))
        problemas = verificar_usuarios_inseguros()
        
        if problemas:
            self.stdout.write(self.style.ERROR(f'\n⚠️  Encontrados {len(problemas)} usuário(s) com problemas:\n'))
            for item in problemas:
                usuario = item['usuario']
                self.stdout.write(
                    self.style.WARNING(f'  • Usuário: {usuario.username} (ID: {usuario.id})')
                )
                for problema in item['problemas']:
                    self.stdout.write(self.style.ERROR(f'    - {problema}'))
                
                if options['corrigir']:
                    if 'Usuário padrão perigoso' in item['problemas']:
                        usuario.is_active = False
                        usuario.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Usuário {usuario.username} desabilitado')
                        )
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Nenhum problema encontrado'))
        
        # 2. Desabilita usuários padrão
        if options['desabilitar_padrao'] or options['corrigir']:
            self.stdout.write(self.style.SUCCESS('\n2. Desabilitando usuários padrão perigosos...'))
            desabilitados = desabilitar_usuarios_padrao()
            if desabilitados:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {len(desabilitados)} usuário(s) desabilitado(s): {", ".join(desabilitados)}')
                )
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ Nenhum usuário padrão encontrado'))
        
        # 3. Lista todos os superusuários
        self.stdout.write(self.style.SUCCESS('\n3. Verificando superusuários...'))
        superusuarios = User.objects.filter(is_superuser=True)
        if superusuarios.exists():
            self.stdout.write(self.style.WARNING(f'  ⚠️  Encontrados {superusuarios.count()} superusuário(s):'))
            for su in superusuarios:
                status = 'ATIVO' if su.is_active else 'INATIVO'
                self.stdout.write(
                    self.style.WARNING(f'    • {su.username} ({su.email}) - {status}')
                )
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Nenhum superusuário encontrado'))
        
        # 4. Verifica usuários sem senha
        self.stdout.write(self.style.SUCCESS('\n4. Verificando usuários sem senha...'))
        usuarios_sem_senha = [u for u in User.objects.all() if not u.has_usable_password() and u.is_active]
        if usuarios_sem_senha:
            self.stdout.write(self.style.ERROR(f'  ⚠️  {len(usuarios_sem_senha)} usuário(s) ativo(s) sem senha:'))
            for u in usuarios_sem_senha:
                self.stdout.write(self.style.ERROR(f'    • {u.username}'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Todos os usuários ativos têm senha'))
        
        # 5. Recomendações
        self.stdout.write(self.style.SUCCESS('\n=== RECOMENDAÇÕES DE SEGURANÇA ===\n'))
        self.stdout.write('1. Certifique-se de que não há usuários com senhas padrão (admin, 123456, etc)')
        self.stdout.write('2. Desabilite ou remova usuários padrão como "admin", "test", "demo"')
        self.stdout.write('3. Use senhas fortes (mínimo 12 caracteres, com maiúsculas, minúsculas, números e símbolos)')
        self.stdout.write('4. Ative HTTPS em produção')
        self.stdout.write('5. Mantenha o Django e dependências atualizados')
        self.stdout.write('6. Use variáveis de ambiente para SECRET_KEY e senhas de banco de dados')
        self.stdout.write('\nPara corrigir automaticamente, execute:')
        self.stdout.write(self.style.WARNING('  python manage.py verificar_seguranca --corrigir --desabilitar-padrao\n'))







