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
    planos = PlanoAssinatura.objects.filter(ativo=True).order_by("preco_mensal_referencia", "nome")
    assinatura = (
        AssinaturaCliente.objects.select_related("plano")
        .filter(usuario=request.user)
        .first()
    )
    workspace = getattr(assinatura, "workspace", None) if assinatura else None
    # Determinar gateway padrão (apenas Mercado Pago)
    gateway_default = getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
    
    # Obter chave pública do gateway
    publishable_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
    
    contexto = {
        "planos": planos,
        "assinatura": assinatura,
        "publishable_key": publishable_key,
        "gateway": gateway_default,
        "workspace": workspace,
    }
    return render(request, "gestao_rural/assinaturas_dashboard.html", contexto)


@login_required
@csrf_exempt
def iniciar_checkout(request: HttpRequest, plano_slug: str) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    # Validações de segurança
    from .security_avancado import (
        verificar_assinatura_ativa_para_pagamento,
        registrar_log_auditoria,
        obter_ip_address,
    )
    
    ip_address = obter_ip_address(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Verificar se pode processar pagamento (permitir se não tiver assinatura ou se estiver inativa)
    try:
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
    except Exception as e:
        # Se houver erro na verificação, permite continuar (não bloqueia)
        import traceback
        traceback.print_exc()
        pass

    plano = get_object_or_404(PlanoAssinatura, slug=plano_slug, ativo=True)
    assinatura, _ = AssinaturaCliente.objects.get_or_create(
        usuario=request.user, defaults={"plano": plano}
    )
    assinatura.plano = plano
    assinatura.status = AssinaturaCliente.Status.PENDENTE
    assinatura.save(update_fields=["plano", "status", "atualizado_em"])
    
    # Registrar log
    registrar_log_auditoria(
        tipo_acao='PROCESSAR_PAGAMENTO',
        descricao=f"Iniciado checkout para plano {plano.nome}",
        usuario=request.user,
        ip_address=ip_address,
        user_agent=user_agent,
        nivel_severidade='MEDIO',
        metadata={'plano_id': plano.id, 'plano_slug': plano_slug},
    )

    success_url = request.build_absolute_uri(reverse("assinaturas_sucesso"))
    cancel_url = request.build_absolute_uri(reverse("assinaturas_cancelado"))

    # Determinar gateway a usar (pode ser passado via parâmetro ou usar padrão)
    gateway_name = request.POST.get('gateway') or request.GET.get('gateway') or getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
    
    try:
        # Criar instância do gateway usando factory
        gateway = PaymentGatewayFactory.criar_gateway(gateway_name)
        
        # Verificar se o gateway foi criado
        if not gateway:
            return JsonResponse({"detail": f"Gateway '{gateway_name}' não pôde ser criado. Verifique as configurações."}, status=500)
        
        # Definir gateway na assinatura
        assinatura.gateway_pagamento = gateway_name
        assinatura.save(update_fields=["gateway_pagamento", "atualizado_em"])
        
        # Criar sessão de checkout
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
        traceback.print_exc()
        error_msg = f"Erro ao iniciar checkout: {exc}"
        return JsonResponse({"detail": error_msg}, status=500)

    return JsonResponse({"checkout_url": session_result.url, "session_id": session_result.session_id})


@login_required
def checkout_sucesso(request: HttpRequest) -> HttpResponse:
    messages.success(
        request,
        "Pagamento recebido! Estamos provisionando seu ambiente. Você receberá um e-mail quando estiver pronto.",
    )
    return redirect("assinaturas_dashboard")


@login_required
def checkout_cancelado(request: HttpRequest) -> HttpResponse:
    messages.info(
        request,
        "Pagamento cancelado. Se precisar de ajuda, entre em contato com o suporte.",
    )
    return redirect("assinaturas_dashboard")


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Webhook para eventos da Stripe - REMOVIDO (usando apenas Mercado Pago)."""
    return HttpResponseBadRequest("Stripe foi removido. Use o webhook do Mercado Pago: /assinaturas/webhook/mercadopago/")


@csrf_exempt
def mercadopago_webhook(request: HttpRequest) -> HttpResponse:
    """Webhook para eventos do Mercado Pago."""
    if request.method != "POST":
        return HttpResponseBadRequest("Método não permitido.")

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
                assinatura = AssinaturaCliente.objects.get(id=external_reference)
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
            # Definir data de liberação como 01/02/2026 se não estiver definida
            if not assinatura.data_liberacao:
                from datetime import date
                assinatura.data_liberacao = date(2026, 2, 1)  # 01/02/2026
                assinatura.save(update_fields=['data_liberacao', 'atualizado_em'])
            
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
O sistema MONPEC estará disponível a partir de 01/02/2026.

SUAS CREDENCIAIS DE ACESSO:
Email: {email_usuario}
Senha: monpec01022026

IMPORTANTE:
- Este é um sistema de pré-lançamento
- O acesso será liberado em 01/02/2026
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
            <p>O sistema MONPEC estará disponível a partir de <strong>01/02/2026</strong>.</p>
        </div>
        
        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">🔐 SUAS CREDENCIAIS DE ACESSO</h3>
            <p><strong>Email:</strong> {email_usuario}</p>
            <p><strong>Senha:</strong> monpec01022026</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ IMPORTANTE:</strong>
            <ul>
                <li>Este é um sistema de pré-lançamento</li>
                <li>O acesso será liberado em <strong>01/02/2026</strong></li>
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
        assinatura = AssinaturaCliente.objects.select_related('plano').get(usuario=request.user)
    except AssinaturaCliente.DoesNotExist:
        return redirect('assinaturas_dashboard')
    
    # Redirecionar para dashboard de demonstração
    return redirect('dashboard')


# Funções de handlers do Stripe removidas - usando apenas Mercado Pago

