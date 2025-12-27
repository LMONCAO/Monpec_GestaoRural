# -*- coding: utf-8 -*-
"""
Comando para limpar todos os usuários exceto admin
python manage.py limpar_usuarios
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Remove todos os usuários exceto admin e define senha do admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--senha-admin',
            type=str,
            default='L6171r12@@',
            help='Senha para o usuário admin (padrão: L6171r12@@)'
        )
        parser.add_argument(
            '--username-admin',
            type=str,
            default='admin',
            help='Username do admin (padrão: admin)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem perguntar'
        )

    def handle(self, *args, **options):
        senha_admin = options['senha_admin']
        username_admin = options['username_admin']
        confirmar = options['confirmar']
        
        # Contar usuários
        total_usuarios = User.objects.count()
        usuarios_para_excluir = User.objects.exclude(username=username_admin).count()
        
        self.stdout.write(f'Total de usuários: {total_usuarios}')
        self.stdout.write(f'Usuários a serem excluídos: {usuarios_para_excluir}')
        self.stdout.write(f'Usuário admin a ser mantido: {username_admin}')
        
        if not confirmar:
            resposta = input('\nTem certeza que deseja excluir todos os usuários exceto admin? (sim/não): ')
            if resposta.lower() not in ['sim', 's', 'yes', 'y']:
                self.stdout.write(self.style.WARNING('Operação cancelada.'))
                return
        
        try:
            with transaction.atomic():
                # Obter ou criar admin
                admin, created = User.objects.get_or_create(
                    username=username_admin,
                    defaults={
                        'email': 'admin@monpec.com.br',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                
                if not created:
                    # Atualizar admin existente
                    admin.is_staff = True
                    admin.is_superuser = True
                    admin.is_active = True
                    admin.email = 'admin@monpec.com.br'
                    admin.save()
                
                # Definir senha do admin
                admin.set_password(senha_admin)
                admin.save()
                
                self.stdout.write(self.style.SUCCESS(f'✅ Senha do admin "{username_admin}" definida com sucesso!'))
                
                # Excluir todos os outros usuários
                usuarios_excluidos = User.objects.exclude(username=username_admin).delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f'✅ {usuarios_excluidos[0]} usuário(s) excluído(s) com sucesso!'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Apenas o usuário "{username_admin}" foi mantido.'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao limpar usuários: {e}'))
            raise


