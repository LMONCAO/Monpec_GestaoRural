import logging
from typing import Iterable

from django.conf import settings  # type: ignore
from django.core.mail import send_mail  # type: ignore


logger = logging.getLogger(__name__)


def _remetente_padrao() -> str | None:
    if hasattr(settings, "DEFAULT_FROM_EMAIL") and settings.DEFAULT_FROM_EMAIL:
        return settings.DEFAULT_FROM_EMAIL
    if hasattr(settings, "EMAIL_HOST_USER") and settings.EMAIL_HOST_USER:
        return settings.EMAIL_HOST_USER
    return None


def enviar_notificacao_compra(assunto: str, mensagem: str, destinatarios: Iterable[str]) -> bool:
    """
    Envia e-mail de notificação para eventos do módulo de compras.

    Retorna True quando pelo menos um envio é realizado; caso contrário, False.
    """
    emails = [email for email in destinatarios if email]
    if not emails:
        logger.debug("Nenhum destinatário válido informado para a notificação: %s", assunto)
        return False

    remetente = _remetente_padrao()
    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=remetente,
            recipient_list=emails,
            fail_silently=False,
        )
        logger.info("Notificação de compras enviada para %s", emails)
        return True
    except Exception:  # pragma: no cover - registro de falha
        logger.exception("Falha ao enviar notificação de compras para %s", emails)
        return False


def _destinatarios_alerta_assinatura() -> list[str]:
    if hasattr(settings, "STRIPE_ALERT_EMAILS"):
        return list(getattr(settings, "STRIPE_ALERT_EMAILS") or [])
    return []


def notificar_evento_assinatura(assinatura, assunto: str, mensagem: str) -> bool:
    """Notifica o time interno sobre eventos críticos de assinatura Stripe."""
    emails = _destinatarios_alerta_assinatura()
    if not emails:
        logger.warning(
            "Alerta de assinatura sem destinatários configurados: %s | %s",
            assunto,
            mensagem,
        )
        return False

    remetente = _remetente_padrao()
    try:
        corpo = (
            f"Assinatura ID: {assinatura.id}\n"
            f"Usuário: {assinatura.usuario}\n"
            f"Plano: {assinatura.plano}\n"
            f"Status atual: {assinatura.get_status_display()}\n\n"
            f"{mensagem}"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=remetente,
            recipient_list=emails,
            fail_silently=False,
        )
        logger.info("Notificação de assinatura enviada para %s: %s", emails, assunto)
        return True
    except Exception:  # pragma: no cover
        logger.exception(
            "Falha ao enviar notificação de assinatura (%s) para %s",
            assunto,
            emails,
        )
        return False

