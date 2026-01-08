"""Classe base abstrata para gateways de pagamento."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.conf import settings

from ...models import AssinaturaCliente, PlanoAssinatura


@dataclass
class CheckoutSessionResult:
    """Resultado da criação de uma sessão de checkout."""
    session_id: str
    url: str
    gateway: str  # Nome do gateway usado (ex: 'mercadopago', 'asaas', 'gerencianet')


class PaymentGateway(ABC):
    """Interface abstrata para gateways de pagamento."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do gateway."""
        pass
    
    @abstractmethod
    def criar_checkout_session(
        self,
        assinatura: AssinaturaCliente,
        plano: PlanoAssinatura,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutSessionResult:
        """
        Cria uma sessão de checkout para o plano informado.
        
        Parameters
        ----------
        assinatura:
            Instância de `AssinaturaCliente` que receberá os dados da sessão.
        plano:
            Plano de assinatura selecionado.
        success_url:
            URL absoluta para redirecionamento após sucesso.
        cancel_url:
            URL absoluta para redirecionamento quando o usuário cancela.
        
        Returns
        -------
        CheckoutSessionResult
            Objeto contendo session_id e url de checkout.
        """
        pass
    
    @abstractmethod
    def processar_webhook(
        self,
        payload: bytes,
        signature_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processa e valida um webhook recebido do gateway.
        
        Parameters
        ----------
        payload:
            Corpo da requisição do webhook.
        signature_header:
            Cabeçalho de assinatura para validação (opcional).
        
        Returns
        -------
        Dict[str, Any]
            Dados do evento processado.
        """
        pass
    
    @abstractmethod
    def atualizar_assinatura_por_evento(
        self,
        assinatura: AssinaturaCliente,
        evento: Dict[str, Any],
    ) -> None:
        """
        Atualiza a assinatura com base em um evento do gateway.
        
        Parameters
        ----------
        assinatura:
            Instância de `AssinaturaCliente` a ser atualizada.
        evento:
            Dados do evento recebido do gateway.
        """
        pass
    
    @abstractmethod
    def cancelar_assinatura(
        self,
        assinatura: AssinaturaCliente,
    ) -> bool:
        """
        Cancela uma assinatura no gateway.
        
        Parameters
        ----------
        assinatura:
            Instância de `AssinaturaCliente` a ser cancelada.
        
        Returns
        -------
        bool
            True se o cancelamento foi bem-sucedido.
        """
        pass
































