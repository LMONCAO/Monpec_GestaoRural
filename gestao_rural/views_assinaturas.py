from __future__ import annotations

from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import AssinaturaCliente, PlanoAssinatura
from .services import notificacoes
from .services.provisionamento import provisionar_workspace
from .services.payments.factory import PaymentGatewayFactory


@login_required
def assinaturas_dashboard(request: HttpRequest) -> HttpResponse:
    """Dashboard de assinaturas - apenas Mercado Pago"""
    from django.db import connection
    
    # Buscar planos ativos
    planos = PlanoAssinatura.objects.filter(ativo=True).order_by("preco_mensal_referencia", "nome")
    
    # Buscar assinatura usando SQL direto para evitar campos do Stripe
    assinatura = None
    try:
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
                # Criar objeto mock com os dados
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
                
                assinatura = AssinaturaMock(row)
                
                # Carregar plano se necessário
                if assinatura.plano_id:
                    try:
                        assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
                    except PlanoAssinatura.DoesNotExist:
                        assinatura.plano = None
    except Exception as e:
        # Se houver erro, continuar sem assinatura
        import traceback
        traceback.print_exc()
        assinatura = None
    
    # Gateway padrão: apenas Mercado Pago
    gateway_default = 'mercadopago'
    publishable_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
    
    contexto = {
        "planos": planos,
        "assinatura": assinatura,
        "publishable_key": publishable_key,
        "gateway": gateway_default,
    }
    return render(request, "gestao_rural/assinaturas_dashboard.html", contexto)


@login_required
@csrf_exempt
def iniciar_checkout(request: HttpRequest, plano_slug: str) -> JsonResponse:
    print(f"DEBUG: Função iniciar_checkout chamada! Método: {request.method}, Plano: {plano_slug}")
    print(f"DEBUG: POST data: {dict(request.POST)}")
    print(f"DEBUG: User: {request.user.username if request.user.is_authenticated else 'Não autenticado'}")
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    # Validações de segurança (opcional - não bloquear se houver erro)
    ip_address = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Verificar se pode processar pagamento (permitir se não tiver assinatura ou se estiver inativa)
    try:
        from .security_avancado import (
            verificar_assinatura_ativa_para_pagamento,
            registrar_log_auditoria,
            obter_ip_address,
        )
        ip_address = obter_ip_address(request)
        pode_processar, mensagem = verificar_assinatura_ativa_para_pagamento(request.user)
        if not pode_processar:
            registrar_log_auditoria(
                tipo_acao='PROCESSAR_PAGAMENTO',
                descricao=f"Tentativa de pagamento bloqueada: {mensagem}",
                usuario=request.user,
                ip_address=ip_address,
                user_agent=user_agent,
                nivel_severidade='ALTO',
                sucesso=False,
            )
            return JsonResponse({"detail": mensagem}, status=400)
    except ImportError:
        # Se o módulo não existir, continuar sem validação
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Módulo security_avancado não encontrado. Continuando sem validação adicional.")
    except Exception as e:
        # Se houver erro na verificação, permite continuar (não bloqueia)
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro na verificação de segurança: {e}")
        traceback.print_exc()
        pass

    plano = get_object_or_404(PlanoAssinatura, slug=plano_slug, ativo=True)
    
    # Capturar nome e email do formulário (se fornecido)
    nome_cliente = request.POST.get('nome', '').strip() or request.user.get_full_name() or request.user.username
    email_cliente = request.POST.get('email', '').strip() or request.user.email
    
    # Atualizar dados do usuário se fornecidos
    if nome_cliente and nome_cliente != request.user.get_full_name():
        partes_nome = nome_cliente.split(' ', 1)
        request.user.first_name = partes_nome[0]
        if len(partes_nome) > 1:
            request.user.last_name = partes_nome[1]
        request.user.save(update_fields=['first_name', 'last_name'])
    
    if email_cliente and email_cliente != request.user.email:
        request.user.email = email_cliente
        request.user.save(update_fields=['email'])
    
    # Usar get_or_create sem only() para evitar problemas com campos removidos
    assinatura, _ = AssinaturaCliente.objects.get_or_create(
        usuario=request.user, defaults={"plano": plano}
    )
    assinatura.plano = plano
    assinatura.status = AssinaturaCliente.Status.PENDENTE
    assinatura.save(update_fields=["plano", "status", "atualizado_em"])
    
    # Registrar log (TEMPORARIAMENTE DESABILITADO para debug)
    # try:
    #     from .security_avancado import registrar_log_auditoria
    #     registrar_log_auditoria(
    #         tipo_acao='PROCESSAR_PAGAMENTO',
    #         descricao=f"Iniciado checkout para plano {plano.nome}",
    #         usuario=request.user,
    #         ip_address=ip_address,
    #         user_agent=user_agent,
    #         nivel_severidade='MEDIO',
    #         metadata={'plano_id': plano.id, 'plano_slug': plano_slug},
    #     )
    # except (ImportError, Exception):
    #     # Se não conseguir registrar log, continuar mesmo assim
    #     pass
    pass

    success_url = request.build_absolute_uri(reverse("assinaturas_sucesso"))
    cancel_url = request.build_absolute_uri(reverse("assinaturas_cancelado"))

    # Determinar gateway a usar (pode ser passado via parâmetro ou usar padrão)
    gateway_name = request.POST.get('gateway') or request.GET.get('gateway') or getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
    
    try:
        # Verificar se o token está configurado antes de criar o gateway
        from decouple import config as decouple_config
        token_check = decouple_config('MERCADOPAGO_ACCESS_TOKEN', default='')
        if not token_check:
            # Tentar via settings também
            token_check = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')

        if not token_check:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("MERCADOPAGO_ACCESS_TOKEN não encontrado em .env nem em settings")
            return JsonResponse({
                "detail": "Configuração do Mercado Pago não encontrada. Entre em contato com o suporte para configurar o sistema de pagamentos."
            }, status=500)
        
        # Criar instância do gateway usando factory
        gateway = PaymentGatewayFactory.criar_gateway(gateway_name)
        
        # Verificar se o gateway foi criado
        if not gateway:
            return JsonResponse({"detail": f"Gateway '{gateway_name}' não pôde ser criado. Verifique as configurações."}, status=500)
        
        # Definir gateway na assinatura
        assinatura.gateway_pagamento = gateway_name
        assinatura.save(update_fields=["gateway_pagamento", "atualizado_em"])
        
        # Criar sessão de checkout (nome e email já foram atualizados no usuário acima)
        session_result = gateway.criar_checkout_session(
            assinatura=assinatura,
            plano=plano,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Verificar se a URL foi gerada
        if not session_result or not session_result.url:
            return JsonResponse({
                "detail": "Erro: URL de checkout não foi gerada. Verifique se MERCADOPAGO_ACCESS_TOKEN está configurado corretamente."
            }, status=500)
            
    except ValueError as exc:
        import traceback
        traceback.print_exc()
        error_msg = str(exc)
        if "não está registrado" in error_msg:
            error_msg += f" Verifique se o gateway '{gateway_name}' está instalado e configurado."
        return JsonResponse({"detail": error_msg}, status=400)
    except RuntimeError as exc:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"RuntimeError ao criar checkout: {exc}", exc_info=True)
        traceback.print_exc()
        error_msg = str(exc)
        if "MERCADOPAGO_ACCESS_TOKEN" in error_msg:
            error_msg += " Configure a variável MERCADOPAGO_ACCESS_TOKEN no arquivo .env"
        return JsonResponse({"detail": error_msg}, status=500)
    except Exception as exc:  # pragma: no cover - logar em produção
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao iniciar checkout: {exc}", exc_info=True)
        traceback.print_exc()
        error_msg = f"Erro ao iniciar checkout: {str(exc)}"
        # Não expor detalhes técnicos ao usuário em produção
        if settings.DEBUG:
            error_msg = f"Erro ao iniciar checkout: {str(exc)}\n\nTraceback:\n{traceback.format_exc()}"
        else:
            error_msg = "Erro ao processar pagamento. Por favor, tente novamente ou entre em contato com o suporte."
        return JsonResponse({"detail": error_msg}, status=500)

    return JsonResponse({"checkout_url": session_result.url, "session_id": session_result.session_id})


@login_required
def checkout_sucesso(request: HttpRequest) -> HttpResponse:
    """Página de confirmação de pagamento com dados de acesso."""
    try:
        assinatura = AssinaturaCliente.objects.filter(usuario=request.user).values(
            'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
            'mercadopago_customer_id', 'mercadopago_subscription_id',
            'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
            'cancelamento_agendado', 'metadata', 'data_liberacao',
            'criado_em', 'atualizado_em'
        ).first()
        # Carregar plano separadamente se necessário
        if assinatura and assinatura.plano_id:
            try:
                assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
            except PlanoAssinatura.DoesNotExist:
                assinatura.plano = None
        
        # Se a assinatura está ativa, mostrar dados de acesso
        if assinatura.status == AssinaturaCliente.Status.ATIVA:
            # Garantir que o usuário tenha a senha padrão
            garantir_senha_padrao_usuario(request.user)
            
            contexto = {
                'assinatura': assinatura,
                'email': request.user.email,
                'senha': 'Monpec2025@',
                'data_liberacao': assinatura.data_liberacao or '01/02/2025',
            }
            return render(request, 'gestao_rural/assinaturas_confirmacao.html', contexto)
        else:
            # Se ainda está pendente, mostrar mensagem de aguardo com informações de contato
            messages.success(
                request,
                f"Pagamento recebido! Estamos processando sua assinatura. Um de nossos consultores entrará em contato em breve através do e-mail {request.user.email} para orientá-lo sobre o sistema.",
            )
            return redirect("assinaturas_dashboard")
    except AssinaturaCliente.DoesNotExist:
        messages.warning(request, "Assinatura não encontrada.")
        return redirect("assinaturas_dashboard")


@login_required
def checkout_cancelado(request: HttpRequest) -> HttpResponse:
    messages.info(
        request,
        "Pagamento cancelado. Se precisar de ajuda, entre em contato com o suporte.",
    )
    return redirect("assinaturas_dashboard")


@csrf_exempt
def mercadopago_webhook(request: HttpRequest) -> HttpResponse:
    """Webhook para eventos do Mercado Pago."""
    if request.method != "POST":
        return HttpResponse(
            "✅ Webhook do Mercado Pago está funcionando!\n\n"
            "Este endpoint aceita apenas requisições POST do Mercado Pago.\n"
            "Acesse via navegador não é permitido por segurança.\n\n"
            "URL configurada corretamente para: https://monpec.com.br/assinaturas/webhook/mercadopago/",
            content_type="text/plain; charset=utf-8",
            status=405
        )

    payload = request.body
    
    try:
        gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
        evento = gateway.processar_webhook(payload)
    except (ValueError, RuntimeError) as exc:
        return HttpResponse(str(exc), status=400)
    except Exception:
        return HttpResponseBadRequest("Evento inválido.")

    tipo_evento = evento.get("type")
    dados = evento.get("data", {})
    
    # Buscar assinatura pelo external_reference ou preapproval_id
    assinatura = None
    
    if tipo_evento == "payment":
        external_reference = dados.get("external_reference")
        if external_reference:
            try:
                assinatura = AssinaturaCliente.objects.filter(id=external_reference).values(
            'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
            'mercadopago_customer_id', 'mercadopago_subscription_id',
            'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
            'cancelamento_agendado', 'metadata', 'data_liberacao',
            'criado_em', 'atualizado_em'
        ).first()
            except AssinaturaCliente.DoesNotExist:
                pass
    elif tipo_evento in ["subscription", "preapproval"]:
        preapproval_id = dados.get("id")
        if preapproval_id:
            # Buscar por metadata
            assinatura = AssinaturaCliente.objects.filter(
                metadata__mercadopago_preapproval_id=preapproval_id
            ).first()
    
    if assinatura:
        gateway.atualizar_assinatura_por_evento(assinatura, evento)
        assinatura.refresh_from_db()
        
        if assinatura.status == AssinaturaCliente.Status.ATIVA:
            # Definir data de liberação como 01/02/2025 se não estiver definida
            if not assinatura.data_liberacao:
                from datetime import date
                assinatura.data_liberacao = date(2025, 2, 1)  # 01/02/2025
                assinatura.save(update_fields=['data_liberacao', 'atualizado_em'])
            
            # Garantir que o usuário tenha a senha padrão definida
            garantir_senha_padrao_usuario(assinatura.usuario)
            
            # Confirmar email e telefone automaticamente quando pagamento é confirmado
            confirmar_email_e_telefone_usuario(assinatura.usuario)
            
            resultado = provisionar_workspace(assinatura)
            
            # Enviar email com credenciais de acesso apenas na primeira ativação
            if not assinatura.metadata or not assinatura.metadata.get('email_enviado'):
                enviar_email_confirmacao_assinatura(assinatura)
                # Marcar que email foi enviado
                if not assinatura.metadata:
                    assinatura.metadata = {}
                assinatura.metadata['email_enviado'] = True
                assinatura.save(update_fields=['metadata', 'atualizado_em'])
    
    return HttpResponse(status=200)


def garantir_senha_padrao_usuario(usuario) -> None:
    """Garante que o usuário tenha a senha padrão Monpec2025@ definida."""
    from django.contrib.auth.hashers import check_password
    
    senha_padrao = "Monpec2025@"
    
    # Verificar se o usuário já tem senha definida
    if usuario.password and len(usuario.password) > 0:
        # Se já tem senha, verificar se é a padrão
        if not check_password(senha_padrao, usuario.password):
            # Se não for a padrão, definir a senha padrão
            usuario.set_password(senha_padrao)
            usuario.save(update_fields=['password'])
    else:
        # Se não tem senha, definir a padrão
        usuario.set_password(senha_padrao)
        usuario.save(update_fields=['password'])


def confirmar_email_e_telefone_usuario(usuario) -> None:
    """
    Confirma automaticamente email e telefone do usuário quando o pagamento é confirmado.
    Isso garante que usuários que pagaram não precisem verificar manualmente.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models_auditoria import VerificacaoEmail, UsuarioAtivo
    
    # Confirmar email
    try:
        verificacao_email, created = VerificacaoEmail.objects.get_or_create(
            usuario=usuario,
            defaults={
                'token': 'auto-confirmed-payment',
                'email_verificado': True,
                'token_expira_em': timezone.now() + timedelta(days=365),  # Longo prazo
                'verificado_em': timezone.now(),
            }
        )
        
        # Se já existe, apenas marcar como verificado
        if not created and not verificacao_email.email_verificado:
            verificacao_email.email_verificado = True
            verificacao_email.verificado_em = timezone.now()
            verificacao_email.save(update_fields=['email_verificado', 'verificado_em'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao confirmar email do usuário {usuario.id}: {e}")
    
    # Ativar usuário se ainda não estiver ativo
    if not usuario.is_active:
        usuario.is_active = True
        usuario.save(update_fields=['is_active'])
    
    # Confirmar telefone (se houver registro em UsuarioAtivo)
    try:
        usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
            usuario=usuario,
            defaults={
                'nome_completo': usuario.get_full_name() or usuario.username,
                'email': usuario.email or '',
                'telefone': '',  # Será preenchido se disponível
                'ativo': True,
            }
        )
        
        # Se já existe, apenas garantir que está ativo
        if not created and not usuario_ativo.ativo:
            usuario_ativo.ativo = True
            usuario_ativo.save(update_fields=['ativo'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao confirmar telefone do usuário {usuario.id}: {e}")


def enviar_email_confirmacao_assinatura(assinatura: AssinaturaCliente) -> bool:
    """Envia email de confirmação de assinatura com credenciais de acesso."""
    try:
        usuario = assinatura.usuario
        email_usuario = usuario.email
        
        assunto = "Assinatura Confirmada - MONPEC - Pré-Lançamento"
        
        mensagem_texto = f"""
Olá {usuario.get_full_name() or usuario.username},

Sua assinatura foi confirmada com sucesso!

ASSINATURA DE PRÉ-LANÇAMENTO
O sistema MONPEC estará disponível a partir de 01/02/2025.

SUAS CREDENCIAIS DE ACESSO:
Email: {email_usuario}
Senha: Monpec2025@

IMPORTANTE:
- Este é um sistema de pré-lançamento
- O acesso será liberado em 01/02/2025
- Um de nossos consultores entrará em contato em breve para orientá-lo sobre o sistema
- Guarde estas credenciais com segurança

Enquanto aguarda o lançamento, você pode acessar a versão de demonstração do sistema para conhecer as funcionalidades.

Atenciosamente,
Equipe MONPEC - Gestão Rural Inteligente
"""
        
        mensagem_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f8f9fa;
            padding: 30px;
            border: 1px solid #dee2e6;
        }}
        .credentials {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #0d6efd;
            border-radius: 5px;
        }}
        .credentials strong {{
            color: #0d6efd;
            font-size: 16px;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Gestão Rural Inteligente</h1>
        <p>Assinatura Confirmada - Pré-Lançamento</p>
    </div>
    
    <div class="content">
        <p>Olá <strong>{usuario.get_full_name() or usuario.username}</strong>,</p>
        
        <p>Sua assinatura foi confirmada com sucesso!</p>
        
        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">📋 ASSINATURA DE PRÉ-LANÇAMENTO</h3>
            <p>O sistema MONPEC estará disponível a partir de <strong>01/02/2025</strong>.</p>
        </div>
        
        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">🔐 SUAS CREDENCIAIS DE ACESSO</h3>
            <p><strong>Email:</strong> {email_usuario}</p>
            <p><strong>Senha:</strong> Monpec2025@</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ IMPORTANTE:</strong>
            <ul>
                <li>Este é um sistema de pré-lançamento</li>
                <li>O acesso será liberado em <strong>01/02/2025</strong></li>
                <li>Um de nossos consultores entrará em contato em breve para orientá-lo sobre o sistema</li>
                <li>Guarde estas credenciais com segurança</li>
            </ul>
        </div>
        
        <p>Enquanto aguarda o lançamento, você pode acessar a versão de demonstração do sistema para conhecer as funcionalidades.</p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe MONPEC - Gestão Rural Inteligente</strong></p>
    </div>
    
    <div class="footer">
        <p>Este é um email automático, por favor não responda.</p>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
</body>
</html>
"""
        
        remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br')
        
        send_mail(
            subject=assunto,
            message=mensagem_texto,
            from_email=remetente,
            recipient_list=[email_usuario],
            html_message=mensagem_html,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Erro ao enviar email de confirmação de assinatura: {e}")
        return False


@login_required
def pre_lancamento(request: HttpRequest) -> HttpResponse:
    """Página de pré-lançamento para assinantes."""
    try:
        assinatura = AssinaturaCliente.objects.filter(usuario=request.user).values(
            'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
            'mercadopago_customer_id', 'mercadopago_subscription_id',
            'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
            'cancelamento_agendado', 'metadata', 'data_liberacao',
            'criado_em', 'atualizado_em'
        ).first()
        # Carregar plano separadamente se necessário
        if assinatura and assinatura.plano_id:
            try:
                assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
            except PlanoAssinatura.DoesNotExist:
                assinatura.plano = None
    except AssinaturaCliente.DoesNotExist:
        return redirect('assinaturas_dashboard')
    
    # Redirecionar para dashboard de demonstração
    return redirect('dashboard')


# Sistema de pagamento: Apenas Mercado Pago
# Stripe foi completamente removido do sistema

