"""Factory para criar instâncias de gateways de pagamento."""

from __future__ import annotations

from django.conf import settings
from typing import Optional

from .base import PaymentGateway


class PaymentGatewayFactory:
    """Factory para criar instâncias de gateways de pagamento."""
    
    _gateways: dict[str, type[PaymentGateway]] = {}
    
    @classmethod
    def registrar_gateway(cls, nome: str, gateway_class: type[PaymentGateway]) -> None:
        """Registra uma classe de gateway."""
        cls._gateways[nome.lower()] = gateway_class
    
    @classmethod
    def criar_gateway(cls, nome: Optional[str] = None) -> PaymentGateway:
        """
        Cria uma instância do gateway especificado.
        
        Parameters
        ----------
        nome:
            Nome do gateway ('stripe', 'mercadopago', 'asaas', etc.).
            Se None, usa o gateway padrão das configurações.
        
        Returns
        -------
        PaymentGateway
            Instância do gateway solicitado.
        
        Raises
        ------
        ValueError
            Se o gateway não estiver registrado ou configurado.
        """
        if nome is None:
            nome = getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
        
        nome = nome.lower()
        
        if nome not in cls._gateways:
            raise ValueError(
                f"Gateway '{nome}' não está registrado. "
                f"Gateways disponíveis: {', '.join(cls._gateways.keys())}"
            )
        
        gateway_class = cls._gateways[nome]
        return gateway_class()
    
    @classmethod
    def listar_gateways_disponiveis(cls) -> list[str]:
        """Retorna lista de gateways registrados."""
        return list(cls._gateways.keys())


# Importar e registrar gateways disponíveis
def _registrar_gateways() -> None:
    """Registra todos os gateways disponíveis."""
    # Removido: Stripe - usando apenas Mercado Pago
    
    # Mercado Pago - sempre registrar
    from .mercadopago_gateway import MercadoPagoGateway
    PaymentGatewayFactory.registrar_gateway('mercadopago', MercadoPagoGateway)
    PaymentGatewayFactory.registrar_gateway('mp', MercadoPagoGateway)  # Alias
    
    # Asaas
    try:
        from .asaas_gateway import AsaasGateway
        PaymentGatewayFactory.registrar_gateway('asaas', AsaasGateway)
    except ImportError:
        pass
    
    # Gerencianet
    try:
        from .gerencianet_gateway import GerencianetGateway
        PaymentGatewayFactory.registrar_gateway('gerencianet', GerencianetGateway)
        PaymentGatewayFactory.registrar_gateway('efi', GerencianetGateway)  # Alias
    except ImportError:
        pass


# Registrar gateways ao importar o módulo
_registrar_gateways()

