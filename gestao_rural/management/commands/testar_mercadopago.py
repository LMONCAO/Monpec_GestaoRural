"""Comando para testar a integração com Mercado Pago."""

from django.core.management.base import BaseCommand
from django.conf import settings
from gestao_rural.services.payments.factory import PaymentGatewayFactory


class Command(BaseCommand):
    help = 'Testa a configuração do Mercado Pago'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testando integração Mercado Pago...\n'))
        
        # Verificar configurações
        self.stdout.write('1. Verificando configurações...')
        
        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
        public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
        gateway_default = getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'stripe')
        
        if not access_token:
            self.stdout.write(self.style.ERROR('   ❌ MERCADOPAGO_ACCESS_TOKEN não configurado'))
            self.stdout.write(self.style.WARNING('   💡 Adicione no .env: MERCADOPAGO_ACCESS_TOKEN=seu_token'))
            return
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ MERCADOPAGO_ACCESS_TOKEN configurado'))
            if access_token.startswith('TEST-'):
                self.stdout.write(self.style.WARNING('   ⚠️  Usando credenciais de TESTE'))
            elif access_token.startswith('APP_USR-'):
                self.stdout.write(self.style.WARNING('   ⚠️  Usando credenciais de PRODUÇÃO'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Formato de token não reconhecido'))
        
        if not public_key:
            self.stdout.write(self.style.WARNING('   ⚠️  MERCADOPAGO_PUBLIC_KEY não configurado (opcional)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ MERCADOPAGO_PUBLIC_KEY configurado'))
        
        self.stdout.write(f'\n2. Gateway padrão: {gateway_default}')
        if gateway_default == 'mercadopago':
            self.stdout.write(self.style.SUCCESS('   ✅ Mercado Pago está configurado como padrão'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Gateway padrão é "{gateway_default}", não "mercadopago"'))
            self.stdout.write(self.style.WARNING('   💡 Adicione no .env: PAYMENT_GATEWAY_DEFAULT=mercadopago'))
        
        # Testar criação do gateway
        self.stdout.write('\n3. Testando criação do gateway...')
        try:
            gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
            self.stdout.write(self.style.SUCCESS('   ✅ Gateway criado com sucesso'))
            self.stdout.write(f'   📝 Nome do gateway: {gateway.name}')
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro ao criar gateway: {e}'))
            return
        except RuntimeError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro de configuração: {e}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro inesperado: {e}'))
            return
        
        # Testar conexão com API
        self.stdout.write('\n4. Testando conexão com API do Mercado Pago...')
        try:
            import mercadopago
            mp = mercadopago.SDK(access_token)
            # Fazer uma requisição simples para testar
            result = mp.payment_methods().list_all()
            if result.get("status") == 200:
                self.stdout.write(self.style.SUCCESS('   ✅ Conexão com API OK'))
                methods = result.get("response", [])
                self.stdout.write(f'   📊 Métodos de pagamento disponíveis: {len(methods)}')
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ Erro na API: {result.get("message")}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro ao conectar: {e}'))
            self.stdout.write(self.style.WARNING('   💡 Verifique se o Access Token está correto'))
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Teste concluído!'))
        self.stdout.write('\n📋 Próximos passos:')
        self.stdout.write('   1. Execute as migrações: python manage.py migrate')
        self.stdout.write('   2. Configure os planos no admin')
        self.stdout.write('   3. Teste o checkout em: http://localhost:8000/assinaturas/')
        self.stdout.write('\n📚 Documentação: docs/GUIA_RAPIDO_MERCADOPAGO.md')































