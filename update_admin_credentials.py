#!/usr/bin/env python3
"""
SCRIPT PARA ATUALIZAR SENHA DO ADMIN - VERSÃO GOOGLE CLOUD
Executa no Google Cloud para alterar senha do administrador
"""
import os
import sys

# Configurar Django para Google Cloud
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')

# Verificar se estamos no ambiente correto
if len(sys.argv) > 1:
    # Se passou senha como argumento (para execução no Cloud)
    nova_senha = sys.argv[1]

    import django
    django.setup()
    from django.contrib.auth.models import User

    print('🔐 Atualizando senha do admin no Google Cloud...')

    # Encontrar usuário admin
    admin_user = User.objects.filter(username='admin').first()

    if admin_user:
        admin_user.set_password(nova_senha)
        admin_user.save()
        print('✅ Senha atualizada com sucesso!')
        print(f'👤 Usuário: admin')
        print(f'📧 Email: admin@monpec.com.br')
    else:
        print('❌ Usuário admin não encontrado!')

else:
    # Versão interativa local
    import getpass
    import django
    django.setup()
    from django.contrib.auth.models import User

    print('🔐 ATUALIZADOR DE SENHA DO ADMINISTRADOR')
    print('=' * 50)

    # Solicitar nova senha
    while True:
        print('\n📝 Digite a nova senha para o usuário admin:')
        print('💡 Recomendações de segurança:')
        print('   • Pelo menos 8 caracteres')
        print('   • Inclua letras maiúsculas e minúsculas')
        print('   • Inclua números e símbolos')
        print('   • Evite senhas comuns como "admin123", "123456", etc.')

        nova_senha = getpass.getpass('Nova senha: ')
        confirmar_senha = getpass.getpass('Confirme a senha: ')

        if nova_senha != confirmar_senha:
            print('❌ As senhas não coincidem. Tente novamente.')
            continue

        # Validar força da senha
        if len(nova_senha) < 8:
            print('❌ A senha deve ter pelo menos 8 caracteres.')
            continue

        # Senha aceita
        break

    print('\n🔍 Verificando usuário admin...')

    # Tentar encontrar usuário admin existente
    admin_user = User.objects.filter(username='admin').first()

    if admin_user:
        print(f'✅ Usuário admin encontrado: {admin_user.username}')

        # Verificar se a senha atual é diferente
        if admin_user.check_password(nova_senha):
            print('⚠️ A nova senha é igual à senha atual.')
            resposta = input('Deseja continuar mesmo assim? (s/n): ')
            if resposta.lower() != 's':
                print('❌ Operação cancelada.')
                exit(0)

        # Atualizar senha
        admin_user.set_password(nova_senha)
        admin_user.save()
        print('✅ Senha atualizada com sucesso!')

    else:
        print('❌ Usuário admin não encontrado')
        # Criar novo superusuário
        print('👤 Criando novo superusuário...')
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@monpec.com.br',
            password=nova_senha,
            first_name='Administrador',
            last_name='Sistema'
        )
        print('✅ Superusuário criado!')

    print('\n🎉 SENHA ATUALIZADA COM SUCESSO!')
    print('=' * 50)
    print(f'👤 Usuário: admin')
    print(f'📧 Email: admin@monpec.com.br')
    print('🔑 Senha: [OCULTA POR SEGURANÇA]')
    print('')
    print('🌐 Para acessar o sistema:')
    print('   URL: https://monpec.com.br/login/')
    print('   ou: https://monpec-29862706245.us-central1.run.app/login/')
    print('')
    print('⚠️ IMPORTANTE: Anote sua nova senha em local seguro!')
    print('💡 Guarde esta informação pois ela não será exibida novamente.')
