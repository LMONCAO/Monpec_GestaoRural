"""
Middleware para controlar liberação de acesso baseado na data de liberação da assinatura.
Usuários só terão acesso após a data_liberacao definida na assinatura.
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .models import AssinaturaCliente


class LiberacaoAcessoMiddleware(MiddlewareMixin):
    """
    Middleware que verifica se o usuário tem acesso liberado baseado na data_liberacao.
    """
    
    def process_request(self, request):
        """Verifica se o acesso está liberado para o usuário."""
        
        # URLs públicas que não precisam de verificação
        urls_publicas = [
            '/login/',
            '/logout/',
            '/recuperar-senha/',
            '/verificar-email/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/assinaturas/',  # Página de assinaturas sempre acessível
            '/assinaturas/sucesso/',
            '/assinaturas/cancelado/',
            '/assinaturas/webhook/',
            '/pre-lancamento/',  # Página de pré-lançamento
        ]
        
        # Verificar se é URL pública
        if any(request.path.startswith(url) for url in urls_publicas):
            return None
        
        # Verificar apenas usuários autenticados
        if not request.user.is_authenticated:
            return None
        
        # Importar funções helper
        from .helpers_acesso import is_usuario_demo, is_usuario_assinante
        
        # CRÍTICO: Verificar se é usuário demo PRIMEIRO (antes de verificar assinatura)
        # Usuários demo NUNCA são assinantes, mesmo que tenham assinatura no banco
        is_demo_user = is_usuario_demo(request.user)
        
        # Se for usuário demo, tratar como demo (acesso restrito)
        if is_demo_user:
            request.assinatura = None
            request.acesso_liberado = False  # Usuários demo têm acesso restrito
            # Permitir acesso apenas a algumas rotas específicas
            if not any(request.path.startswith(path) for path in [
                '/propriedade/', '/dashboard/', '/demo/setup/', 
                '/login/', '/logout/', '/static/', '/media/'
            ]):
                return None  # Continuar normalmente, mas acesso_liberado será False
            return None
        
        # Verificar se é admin - só admin tem acesso completo ao sistema
        if request.user.is_superuser or request.user.is_staff:
            # Admin tem acesso completo
            request.assinatura = None
            request.acesso_liberado = True
            return None  # Permitir acesso completo

        # Verificar se é assinante ativo - redirecionar para área do assinante
        if is_usuario_assinante(request.user):
            # Usuário ativo - redirecionar para área do assinante
            if request.path not in ['/area-assinante/', '/logout/', '/static/', '/media/']:
                messages.info(request, 'Bem-vindo! Você está sendo direcionado para sua área personalizada.')
                return redirect('area_assinante')
            # Se já estiver na área do assinante, permitir acesso
            request.assinatura = None
            request.acesso_liberado = True
            return None
        
        # Verificar se o usuário tem assinatura (mas não é assinante ativo)
        try:
            # Usar SQL direto para evitar campos do Stripe
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, usuario_id, produtor_id, plano_id, status,
                           mercadopago_customer_id, mercadopago_subscription_id,
                           gateway_pagamento, ultimo_checkout_id, current_period_end,
                           cancelamento_agendado, metadata, data_liberacao,
                           criado_em, atualizado_em
                    FROM gestao_rural_assinaturacliente
                    WHERE usuario_id = %s
                    LIMIT 1
                """, [request.user.id])
                row = cursor.fetchone()
                if row:
                    class AssinaturaMock:
                        def __init__(self, row_data):
                            self.id = row_data[0]
                            self.usuario_id = row_data[1]
                            self.produtor_id = row_data[2]
                            self.plano_id = row_data[3]
                            self.status = row_data[4]
                            self.mercadopago_customer_id = row_data[5]
                            self.mercadopago_subscription_id = row_data[6]
                            self.gateway_pagamento = row_data[7]
                            self.ultimo_checkout_id = row_data[8]
                            self.current_period_end = row_data[9]
                            self.cancelamento_agendado = row_data[10]
                            self.metadata = row_data[11]
                            self.data_liberacao = row_data[12]
                            self.criado_em = row_data[13]
                            self.atualizado_em = row_data[14]
                            self.plano = None
                            # Propriedades necessárias
                            from datetime import date
                            self.acesso_liberado = row_data[12] is None or row_data[12] <= date.today()
                    assinatura = AssinaturaMock(row)
                    # Carregar plano se necessário
                    if assinatura.plano_id:
                        try:
                            from .models import PlanoAssinatura
                            assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
                        except:
                            pass
                    request.assinatura = assinatura
                    
                    # Se tiver assinatura ativa mas não passou na verificação de is_usuario_assinante,
                    # significa que não tem acesso_liberado = True
                    if assinatura.status == 'ATIVA' and not assinatura.acesso_liberado:
                        # Assinatura ativa mas sem acesso liberado ainda - pode estar aguardando data de liberação
                        request.acesso_liberado = False
                    elif assinatura.status == 'ATIVA' and assinatura.acesso_liberado:
                        # Se chegou aqui e tem acesso_liberado, deveria ter passado na verificação acima
                        # Mas por segurança, permitir acesso
                        request.acesso_liberado = True
                    else:
                        request.acesso_liberado = False
                else:
                    raise AssinaturaCliente.DoesNotExist()
        except (AssinaturaCliente.DoesNotExist, Exception):
            # Usuário sem assinatura - marcar no request
            request.assinatura = None
            request.acesso_liberado = False
        
        return None

