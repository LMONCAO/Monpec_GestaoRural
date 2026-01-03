"""Implementação do gateway Mercado Pago."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import mercadopago
from django.conf import settings
from django.utils import timezone

from ...models import AssinaturaCliente, PlanoAssinatura
from .base import CheckoutSessionResult, PaymentGateway


class MercadoPagoGateway(PaymentGateway):
    """Gateway de pagamento Mercado Pago."""
    
    def __init__(self):
        """Inicializa o gateway Mercado Pago."""
        self._mp = None
        self._configurar()
    
    @property
    def name(self) -> str:
        return 'mercadopago'
    
    def _configurar(self) -> None:
        """Configura o SDK do Mercado Pago."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Tentar ler de múltiplas formas
        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
        
        # Se não encontrou, tentar via decouple diretamente
        if not access_token:
            from decouple import config
            access_token = config('MERCADOPAGO_ACCESS_TOKEN', default='')
            logger.info(f"Token lido via decouple: {'✅ Encontrado' if access_token else '❌ Não encontrado'}")
        
        if not access_token:
            logger.error("MERCADOPAGO_ACCESS_TOKEN não encontrado em settings nem via decouple")
            raise RuntimeError(
                "MERCADOPAGO_ACCESS_TOKEN não configurado. "
                "Defina a variável de ambiente antes de usar a integração. "
                "Verifique se o arquivo .env está na raiz do projeto e reinicie o servidor."
            )
        
        logger.info(f"Token configurado: {access_token[:20]}...")
        self._mp = mercadopago.SDK(access_token)
    
    def criar_checkout_session(
        self,
        assinatura: AssinaturaCliente,
        plano: PlanoAssinatura,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutSessionResult:
        """
        Cria uma sessão de checkout no Mercado Pago.
        
        Para assinaturas recorrentes, usa Preapproval (Plano de Assinatura).
        """
        if not self._mp:
            self._configurar()
        
        # Usar preço do plano ou padrão de R$ 99,90
        preco = float(plano.preco_mensal_referencia or 99.90)
        
        # Criar preferência de pagamento simples (checkout direto)
        # Não usar Preapproval por enquanto - apenas pagamento único
        preference_data = {
            "items": [
                {
                    "title": plano.nome,
                    "description": plano.descricao or f"Assinatura {plano.nome}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": preco,
                }
            ],
            "back_urls": {
                "success": success_url,
                "failure": cancel_url,
                "pending": success_url,  # Para PIX e boleto
            },
            # Remover auto_return se causar problemas - o Mercado Pago redireciona automaticamente
            "payment_methods": {
                "excluded_payment_types": [],
                "excluded_payment_methods": [],
                "installments": 12,  # Máximo de parcelas
            },
            "notification_url": self._get_webhook_url(),
            "statement_descriptor": "MONPEC ASSINATURA",
            "external_reference": str(assinatura.id),
            "metadata": {
                "assinatura_id": str(assinatura.id),
                "usuario_id": str(assinatura.usuario_id),
                "plano_slug": plano.slug,
            },
        }
        
        # Tentar usar Preapproval se já estiver configurado (opcional)
        preapproval_id = plano.mercadopago_preapproval_id
        if preapproval_id:
            preference_data["subscription_preapproval"] = {
                "preapproval_plan_id": preapproval_id,
            }
        
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Criando preferência no Mercado Pago para plano {plano.nome}")
            logger.debug(f"Dados da preferência: {preference_data}")
            
            response = self._mp.preference().create(preference_data)
            
            logger.info(f"Resposta do Mercado Pago: status={response.get('status')}")
            logger.debug(f"Resposta completa: {response}")
            
        except Exception as e:
            logger.error(f"Exceção ao criar preferência: {e}", exc_info=True)
            raise RuntimeError(f"Erro ao comunicar com Mercado Pago: {str(e)}")
        
        # Verificar resposta
        status = response.get("status")
        if status not in [200, 201]:
            error_message = response.get("message", "Erro desconhecido")
            error_cause = response.get("cause", [])
            
            logger.error(f"Erro na resposta do Mercado Pago: status={status}, message={error_message}, cause={error_cause}")
            
            if error_cause:
                error_details = "; ".join([str(c.get("description", c)) for c in error_cause])
                error_message = f"{error_message}: {error_details}"
            
            raise RuntimeError(f"Erro ao criar checkout: {error_message}")
        
        preference = response.get("response", {})
        if not preference:
            logger.error(f"Resposta vazia do Mercado Pago. Resposta completa: {response}")
            raise RuntimeError("Resposta vazia do Mercado Pago")
        
        # Buscar URL de checkout em múltiplos campos possíveis
        checkout_url = (
            preference.get("init_point") or 
            preference.get("sandbox_init_point") or
            preference.get("checkout_url") or 
            preference.get("url") or
            preference.get("link")
        )
        
        preference_id = preference.get("id")
        
        logger.info(f"Preferência criada: id={preference_id}, url={checkout_url}")
        
        if not checkout_url:
            logger.error(f"URL de checkout não encontrada. Preferência: {preference}")
            raise RuntimeError(f"URL de checkout não encontrada na resposta do Mercado Pago")
        
        if not preference_id:
            logger.warning(f"Preference ID não encontrado, mas URL existe: {checkout_url}")
            # Gerar um ID temporário se não existir
            preference_id = f"temp_{assinatura.id}"
        
        # Salvar informações na assinatura
        assinatura.ultimo_checkout_id = preference_id
        if not assinatura.metadata:
            assinatura.metadata = {}
        assinatura.metadata['mercadopago_preference_id'] = preference_id
        assinatura.save(update_fields=["ultimo_checkout_id", "metadata", "atualizado_em"])
        
        return CheckoutSessionResult(
            session_id=preference_id,
            url=checkout_url,
            gateway='mercadopago'
        )
    
    def _criar_plano_assinatura(self, plano: PlanoAssinatura) -> str:
        """
        Cria um plano de assinatura recorrente no Mercado Pago (Preapproval).
        
        Returns
        -------
        str
            ID do plano de assinatura criado.
        """
        # Usar preço do plano ou padrão de R$ 99,90
        preco = float(plano.preco_mensal_referencia or 99.90)
        
        preapproval_data = {
            "reason": plano.nome,
            "auto_recurring": {
                "frequency": 1,  # Mensal
                "frequency_type": "months",
                "transaction_amount": preco,
                "currency_id": "BRL",
            },
            "payment_methods_allowed": {
                "payment_types": [
                    {"id": "credit_card"},
                    {"id": "debit_card"},
                ],
                "payment_methods": [],
            },
            "back_url": getattr(settings, 'MERCADOPAGO_SUCCESS_URL', ''),
        }
        
        response = self._mp.preapproval().create(preapproval_data)
        
        if response.get("status") != 201:
            error_message = response.get("message", "Erro ao criar plano de assinatura")
            raise RuntimeError(f"Erro ao criar plano: {error_message}")
        
        preapproval = response.get("response", {})
        preapproval_id = preapproval.get("id")
        
        if not preapproval_id:
            raise RuntimeError("Resposta inválida ao criar plano de assinatura")
        
        return preapproval_id
    
    def _get_webhook_url(self) -> str:
        """Retorna a URL do webhook configurada."""
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/assinaturas/webhook/mercadopago/"
    
    def processar_webhook(
        self,
        payload: bytes,
        signature_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processa e valida um webhook do Mercado Pago.
        
        O Mercado Pago envia notificações via IPN (Instant Payment Notification).
        """
        try:
            data = json.loads(payload.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Payload inválido")
        
        # Mercado Pago envia diferentes tipos de notificações
        # Tipo: payment, subscription, preapproval, etc.
        tipo = data.get("type")
        data_id = data.get("data", {}).get("id")
        
        if not tipo or not data_id:
            raise ValueError("Notificação inválida do Mercado Pago")
        
        # Buscar informações completas da API
        if tipo == "payment":
            response = self._mp.payment().get(data_id)
        elif tipo == "subscription" or tipo == "preapproval":
            response = self._mp.preapproval().get(data_id)
        else:
            raise ValueError(f"Tipo de notificação não suportado: {tipo}")
        
        if response.get("status") != 200:
            raise RuntimeError(f"Erro ao buscar dados: {response.get('message')}")
        
        evento = {
            "type": tipo,
            "data": response.get("response", {}),
            "raw": data,
        }
        
        return evento
    
    def atualizar_assinatura_por_evento(
        self,
        assinatura: AssinaturaCliente,
        evento: Dict[str, Any],
    ) -> None:
        """Atualiza a assinatura com base em um evento do Mercado Pago."""
        tipo = evento.get("type")
        dados = evento.get("data", {})
        
        if tipo == "payment":
            self._processar_pagamento(assinatura, dados)
        elif tipo in ["subscription", "preapproval"]:
            self._processar_assinatura(assinatura, dados)
    
    def _processar_pagamento(
        self,
        assinatura: AssinaturaCliente,
        pagamento: Dict[str, Any],
    ) -> None:
        """Processa um evento de pagamento."""
        status = pagamento.get("status")
        status_detail = pagamento.get("status_detail", "")
        external_reference = pagamento.get("external_reference")
        
        # Verificar se o pagamento é desta assinatura
        if external_reference != str(assinatura.id):
            return
        
        # Mapear status do Mercado Pago para status da assinatura
        if status == "approved":
            assinatura.status = AssinaturaCliente.Status.ATIVA
            
            # Definir data de liberação como 01/02/2025 se não estiver definida
            if not assinatura.data_liberacao:
                from datetime import date
                assinatura.data_liberacao = date(2025, 2, 1)  # 01/02/2025
            
            # Atualizar período
            if not assinatura.current_period_end:
                from datetime import timedelta
                assinatura.current_period_end = timezone.now() + timedelta(days=30)
        elif status == "pending":
            assinatura.status = AssinaturaCliente.Status.PENDENTE
        elif status in ["rejected", "cancelled", "refunded", "charged_back"]:
            assinatura.status = AssinaturaCliente.Status.INADIMPLENTE
        else:
            # Manter status atual se não reconhecermos
            pass
        
        # Salvar informações do pagamento
        if not assinatura.metadata:
            assinatura.metadata = {}
        assinatura.metadata['ultimo_pagamento_mp'] = {
            'id': pagamento.get("id"),
            'status': status,
            'status_detail': status_detail,
            'data': timezone.now().isoformat(),
        }
        
        assinatura.save(update_fields=["status", "metadata", "current_period_end", "atualizado_em"])
    
    def _processar_assinatura(
        self,
        assinatura: AssinaturaCliente,
        preapproval: Dict[str, Any],
    ) -> None:
        """Processa um evento de assinatura/preapproval."""
        status = preapproval.get("status")
        preapproval_id = preapproval.get("id")
        
        # Salvar ID da assinatura no Mercado Pago
        if not assinatura.metadata:
            assinatura.metadata = {}
        assinatura.metadata['mercadopago_preapproval_id'] = preapproval_id
        
        # Mapear status
        status_map = {
            "authorized": AssinaturaCliente.Status.ATIVA,
            "pending": AssinaturaCliente.Status.PENDENTE,
            "paused": AssinaturaCliente.Status.SUSPENSA,
            "cancelled": AssinaturaCliente.Status.CANCELADA,
        }
        
        assinatura.status = status_map.get(status, AssinaturaCliente.Status.PENDENTE)
        
        # Atualizar período e data de liberação
        if status == "authorized":
            # Definir data de liberação como 01/02/2025 se não estiver definida
            if not assinatura.data_liberacao:
                from datetime import date
                assinatura.data_liberacao = date(2025, 2, 1)  # 01/02/2025
            
            from datetime import timedelta
            if not assinatura.current_period_end:
                assinatura.current_period_end = timezone.now() + timedelta(days=30)
        
        assinatura.save(update_fields=["status", "metadata", "current_period_end", "atualizado_em"])
    
    def cancelar_assinatura(
        self,
        assinatura: AssinaturaCliente,
    ) -> bool:
        """Cancela uma assinatura no Mercado Pago."""
        if not self._mp:
            self._configurar()
        
        # Buscar preapproval_id da metadata
        preapproval_id = None
        if assinatura.metadata:
            preapproval_id = assinatura.metadata.get('mercadopago_preapproval_id')
        
        if not preapproval_id:
            return False
        
        try:
            # Cancelar preapproval
            response = self._mp.preapproval().update(preapproval_id, {"status": "cancelled"})
            
            if response.get("status") == 200:
                assinatura.status = AssinaturaCliente.Status.CANCELADA
                assinatura.save(update_fields=["status", "atualizado_em"])
                return True
            return False
        except Exception:
            return False

