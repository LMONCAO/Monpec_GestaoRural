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
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import AssinaturaCliente, PlanoAssinatura
from .services import stripe_client, notificacoes
from .services.provisionamento import provisionar_workspace


@login_required
def assinaturas_dashboard(request: HttpRequest) -> HttpResponse:
    planos = PlanoAssinatura.objects.filter(ativo=True).order_by("preco_mensal_referencia", "nome")
    assinatura = (
        AssinaturaCliente.objects.select_related("plano")
        .filter(usuario=request.user)
        .first()
    )
    workspace = getattr(assinatura, "workspace", None) if assinatura else None
    contexto = {
        "planos": planos,
        "assinatura": assinatura,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "workspace": workspace,
    }
    return render(request, "gestao_rural/assinaturas_dashboard.html", contexto)


@login_required
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
    
    # Verificar se pode processar pagamento
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

    try:
        session_result = stripe_client.criar_checkout_session(
            assinatura=assinatura,
            plano=plano,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except stripe_client.StripeConfigurationError as exc:
        return JsonResponse({"detail": str(exc)}, status=500)
    except Exception as exc:  # pragma: no cover - logar em produção
        return JsonResponse({"detail": f"Erro ao iniciar checkout: {exc}"}, status=500)

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
    if request.method != "POST":
        return HttpResponseBadRequest("Método não permitido.")

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if sig_header is None:
        return HttpResponseBadRequest("Cabeçalho Stripe-Signature ausente.")

    try:
        evento = stripe_client.construir_evento_webhook(payload, sig_header)
    except stripe_client.StripeConfigurationError as exc:
        return HttpResponse(str(exc), status=500)
    except Exception:
        return HttpResponseBadRequest("Evento inválido.")

    dados = evento["data"]["object"]
    tipo_evento = evento["type"]

    handlers: Dict[str, Any] = {
        "checkout.session.completed": _handle_checkout_completed,
        "customer.subscription.created": _handle_subscription_event,
        "customer.subscription.updated": _handle_subscription_event,
        "customer.subscription.deleted": _handle_subscription_deleted,
        "invoice.payment_failed": _handle_invoice_failed,
    }

    handler = handlers.get(tipo_evento)
    if handler:
        handler(dados)

    return HttpResponse(status=200)


def _handle_checkout_completed(dados: Dict[str, Any]) -> None:
    assinatura = stripe_client.confirmar_checkout_session(dados)
    if assinatura:
        assinatura.refresh_from_db()
        resultado = provisionar_workspace(assinatura)
        assunto = "Provisionamento concluído" if resultado.sucesso else "Provisionamento falhou"
        mensagem = resultado.mensagem or "Provisionamento executado."
        notificacoes.notificar_evento_assinatura(assinatura, assunto, mensagem)


def _handle_subscription_event(dados: Dict[str, Any]) -> None:
    assinatura_id = dados.get("metadata", {}).get("assinatura_id")
    if not assinatura_id:
        return

    try:
        assinatura = AssinaturaCliente.objects.select_related("usuario").get(id=assinatura_id)
    except AssinaturaCliente.DoesNotExist:
        return

    stripe_client.atualizar_assinatura_por_evento(assinatura, dados)
    assinatura.refresh_from_db()
    if assinatura.status == AssinaturaCliente.Status.ATIVA:
        resultado = provisionar_workspace(assinatura)
        assunto = "Provisionamento concluído" if resultado.sucesso else "Provisionamento falhou"
        mensagem = resultado.mensagem or "Provisionamento executado."
        notificacoes.notificar_evento_assinatura(assinatura, assunto, mensagem)


def _handle_subscription_deleted(dados: Dict[str, Any]) -> None:
    subscription_id = dados.get("id")
    if not subscription_id:
        return

    assinatura = AssinaturaCliente.objects.filter(stripe_subscription_id=subscription_id).first()
    if not assinatura:
        return

    assinatura.atualizar_status(AssinaturaCliente.Status.CANCELADA)


def _handle_invoice_failed(dados: Dict[str, Any]) -> None:
    subscription_id = dados.get("subscription")
    if not subscription_id:
        return

    assinatura = AssinaturaCliente.objects.filter(stripe_subscription_id=subscription_id).first()
    if not assinatura:
        return

    assinatura.atualizar_status(AssinaturaCliente.Status.INADIMPLENTE)
    motivo = dados.get("failure_message") or "Pagamento não processado pela Stripe."
    notificacoes.notificar_evento_assinatura(
        assinatura,
        "Falha de pagamento Stripe",
        motivo,
    )

