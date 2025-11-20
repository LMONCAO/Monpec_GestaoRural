from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import stripe
from django.conf import settings
from django.utils import timezone

from ..models import AssinaturaCliente, PlanoAssinatura


class StripeConfigurationError(RuntimeError):
    """Erro levantado quando as credenciais da Stripe não estão configuradas."""


def _configurar_stripe() -> None:
    """Define a chave secreta da Stripe se ainda não estiver configurada."""
    if not settings.STRIPE_SECRET_KEY:
        raise StripeConfigurationError(
            "STRIPE_SECRET_KEY não configurada. Defina a variável de ambiente antes de usar a integração."
        )
    if stripe.api_key != settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY


@dataclass
class CheckoutSessionResult:
    session_id: str
    url: str


def criar_checkout_session(
    assinatura: AssinaturaCliente,
    plano: PlanoAssinatura,
    success_url: str,
    cancel_url: str,
) -> CheckoutSessionResult:
    """
    Cria uma sessão de checkout na Stripe para o plano informado.

    Parameters
    ----------
    assinatura:
        Instância de `AssinaturaCliente` que receberá os dados da sessão.
    plano:
        Plano de assinatura (Stripe Price) selecionado.
    success_url:
        URL absoluta para redirecionamento após sucesso.
    cancel_url:
        URL absoluta para redirecionamento quando o usuário cancela.
    """
    _configurar_stripe()

    if not plano.stripe_price_id:
        raise ValueError("O plano selecionado não possui Stripe Price ID configurado.")

    customer = assinatura.stripe_customer_id or None
    metadata = {
        "assinatura_id": str(assinatura.id),
        "usuario_id": str(assinatura.usuario_id),
        "plano_slug": plano.slug,
    }

    session = stripe.checkout.Session.create(
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        customer=customer,
        line_items=[{"price": plano.stripe_price_id, "quantity": 1}],
        metadata=metadata,
        subscription_data={
            "metadata": metadata,
        },
    )

    assinatura.ultimo_checkout_id = session.id
    assinatura.save(update_fields=["ultimo_checkout_id", "atualizado_em"])

    return CheckoutSessionResult(session_id=session.id, url=session.url)


def anexar_customer_a_assinatura(assinatura: AssinaturaCliente, customer_id: str) -> None:
    """Atualiza a assinatura com o identificador do cliente na Stripe."""
    if customer_id and assinatura.stripe_customer_id != customer_id:
        assinatura.stripe_customer_id = customer_id
        assinatura.save(update_fields=["stripe_customer_id", "atualizado_em"])


def atualizar_assinatura_por_evento(
    assinatura: AssinaturaCliente,
    subscription: Dict[str, Any],
) -> None:
    """Atualiza os campos da assinatura a partir de um objeto Subscription."""
    status_map = {
        "active": AssinaturaCliente.Status.ATIVA,
        "trialing": AssinaturaCliente.Status.ATIVA,
        "past_due": AssinaturaCliente.Status.INADIMPLENTE,
        "unpaid": AssinaturaCliente.Status.SUSPENSA,
        "canceled": AssinaturaCliente.Status.CANCELADA,
        "incomplete": AssinaturaCliente.Status.PENDENTE,
        "incomplete_expired": AssinaturaCliente.Status.CANCELADA,
    }

    stripe_status = subscription.get("status", "")
    mapped_status = status_map.get(stripe_status, AssinaturaCliente.Status.PENDENTE)

    current_period_end = subscription.get("current_period_end")
    cancel_at_period_end = subscription.get("cancel_at_period_end", False)
    subscription_id = subscription.get("id", "")

    assinatura.status = mapped_status
    assinatura.stripe_subscription_id = subscription_id or assinatura.stripe_subscription_id
    assinatura.cancelamento_agendado = bool(cancel_at_period_end)
    assinatura.current_period_end = (
        timezone.datetime.fromtimestamp(current_period_end, tz=timezone.utc)
        if current_period_end
        else None
    )
    assinatura.save(
        update_fields=[
            "status",
            "stripe_subscription_id",
            "cancelamento_agendado",
            "current_period_end",
            "atualizado_em",
        ]
    )


def confirmar_checkout_session(session: Dict[str, Any]) -> Optional[AssinaturaCliente]:
    """Confirma uma sessão de checkout concluída."""
    assinatura_id = session.get("metadata", {}).get("assinatura_id")
    if not assinatura_id:
        return None

    try:
        assinatura = AssinaturaCliente.objects.select_related("usuario").get(id=assinatura_id)
    except AssinaturaCliente.DoesNotExist:
        return None

    customer_id = session.get("customer")
    anexar_customer_a_assinatura(assinatura, customer_id)

    subscription = session.get("subscription")
    if isinstance(subscription, str):
        _configurar_stripe()
        subscription = stripe.Subscription.retrieve(subscription)

    if isinstance(subscription, dict):
        atualizar_assinatura_por_evento(assinatura, subscription)

    return assinatura


def construir_evento_webhook(payload: bytes, assinatura_header: str) -> stripe.Event:
    """Constrói e valida o evento recebido via webhook."""
    _configurar_stripe()
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    if not endpoint_secret:
        raise StripeConfigurationError(
            "STRIPE_WEBHOOK_SECRET não configurado. Defina a variável de ambiente e atualize o endpoint no Dashboard Stripe."
        )
    return stripe.Webhook.construct_event(payload, assinatura_header, endpoint_secret)












