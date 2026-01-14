import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

print('=== TESTE DO SISTEMA DE NOTIFICAÇÕES DEMO ===')
print('')

# Simular criação de usuário demo
dados_teste = {
    'nome_completo': 'João Silva',
    'email': 'joao.silva@email.com',
    'telefone': '(11) 99999-9999'
}

print('1. Simulando cadastro de usuário demo...')
print(f'   Nome: {dados_teste["nome_completo"]}')
print(f'   Email: {dados_teste["email"]}')
print(f'   Telefone: {dados_teste["telefone"]}')
print('')

# Testar serviço de notificações
print('2. Testando serviço de notificações...')

try:
    from gestao_rural.services_notificacoes_demo import notificar_cadastro_demo

    sucesso = notificar_cadastro_demo(
        nome_completo=dados_teste['nome_completo'],
        email=dados_teste['email'],
        telefone=dados_teste['telefone'],
        ip_address='192.168.1.100'
    )

    if sucesso:
        print('✅ Notificação enviada com sucesso!')
        print('📧 Verifique o console/terminal do Django para ver o email')
    else:
        print('❌ Falha ao enviar notificação')

except Exception as e:
    print(f'❌ Erro no teste: {e}')

print('')
print('3. Verificando estatísticas...')
try:
    from gestao_rural.services_notificacoes_demo import obter_estatisticas_leads_demo
    stats = obter_estatisticas_leads_demo()
    print(f'   Total de leads: {stats["total_leads"]}')
    print(f'   Leads recentes: {stats["leads_recentes"]}')
    print('✅ Estatísticas funcionando')
except Exception as e:
    print(f'❌ Erro nas estatísticas: {e}')

print('')
print('🎯 SISTEMA DE NOTIFICAÇÕES PRONTO!')
print('Agora você será notificado automaticamente quando usuários demo se cadastrarem.')