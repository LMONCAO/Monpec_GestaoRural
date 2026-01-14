import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings'
django.setup()

from gestao_rural.models import AssinaturaCliente, PlanoAssinatura
from django.contrib.auth.models import User
from gestao_rural.services.payments.factory import PaymentGatewayFactory

print('=== DIAGNÓSTICO COMPLETO DO SISTEMA ===')
print()

# 1. Verificar configurações do Mercado Pago
print('🔧 1. CONFIGURAÇÃO MERCADO PAGO:')
try:
    gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
    print('✅ Gateway criado com sucesso')

    # Testar modo teste
    if hasattr(gateway, '_mp') and gateway._mp == 'TEST_MODE':
        print('✅ Modo teste ativado')
    else:
        print('✅ Modo produção (conectado ao Mercado Pago)')
except Exception as e:
    print('❌ Erro na configuração:', str(e))

print()

# 2. Verificar planos disponíveis
print('📋 2. PLANOS DE ASSINATURA:')
planos = PlanoAssinatura.objects.filter(ativo=True)
print(f'📊 Planos ativos encontrados: {planos.count()}')
for plano in planos:
    print(f'   • {plano.nome}: R$ {plano.preco_mensal_referencia} ({plano.slug})')

print()

# 3. Verificar assinaturas existentes
print('👥 3. ASSINATURAS NO SISTEMA:')
assinaturas = AssinaturaCliente.objects.all()
print(f'📊 Total de assinaturas: {assinaturas.count()}')

ativas = assinaturas.filter(status='ATIVA').count()
pendentes = assinaturas.filter(status='PENDENTE').count()
canceladas = assinaturas.filter(status='CANCELADA').count()

print(f'✅ Ativas: {ativas}')
print(f'⏳ Pendentes: {pendentes}')
print(f'❌ Canceladas: {canceladas}')

print()

# 4. Testar criação de checkout
print('💳 4. CRIAÇÃO DE CHECKOUT:')
try:
    if assinaturas.exists():
        assinatura_teste = assinaturas.filter(status='PENDENTE').first() or assinaturas.first()
        if assinatura_teste:
            plano = assinatura_teste.plano
            success_url = 'https://monpec.com.br/assinaturas/sucesso/'
            cancel_url = 'https://monpec.com.br/assinaturas/cancelado/'

            session = gateway.criar_checkout_session(
                assinatura=assinatura_teste,
                plano=plano,
                success_url=success_url,
                cancel_url=cancel_url
            )

            if session and session.url:
                print('✅ Checkout criado com sucesso')
                print(f'   URL: {session.url[:50]}...')
            else:
                print('❌ Falha na criação do checkout')
    else:
        print('⚠️ Nenhuma assinatura para testar')
except Exception as e:
    print('❌ Erro no checkout:', str(e))

print()

# 5. Verificar templates
print('🎨 5. TEMPLATES DISPONÍVEIS:')
templates = [
    'templates/gestao_rural/assinaturas_confirmacao.html',
    'templates/gestao_rural/assinaturas_dashboard.html'
]

for template in templates:
    if os.path.exists(template):
        print(f'✅ {template.split("/")[-1]} existe')
    else:
        print(f'❌ {template.split("/")[-1]} não encontrado')

print()

# 6. Verificar URLs
print('🔗 6. URLs CONFIGURADAS:')
from django.urls import reverse
try:
    urls = [
        ('assinaturas_dashboard', 'Dashboard de assinaturas'),
        ('assinaturas_sucesso', 'Página de sucesso'),
        ('assinaturas_cancelado', 'Página de cancelamento'),
        ('mercadopago_webhook', 'Webhook Mercado Pago')
    ]

    for url_name, description in urls:
        try:
            url = reverse(url_name)
            print(f'✅ {description}: /{url_name}/')
        except:
            print(f'❌ {description}: URL não encontrada')

except Exception as e:
    print('❌ Erro ao verificar URLs:', str(e))

print()

# 7. Verificar funcionalidades especiais
print('⚙️ 7. FUNCIONALIDADES ESPECIAIS:')

# Provisionamento
try:
    from gestao_rural.services.provisionamento import provisionar_workspace
    print('✅ Módulo de provisionamento importado')
except ImportError:
    print('❌ Módulo de provisionamento não encontrado')

# Notificações
try:
    from gestao_rural.services import notificacoes
    print('✅ Sistema de notificações disponível')
except ImportError:
    print('❌ Sistema de notificações não encontrado')

# Email
try:
    from django.core.mail import send_mail
    print('✅ Sistema de email do Django configurado')
except ImportError:
    print('❌ Sistema de email não disponível')

print()
print('=== FIM DO DIAGNÓSTICO ===')