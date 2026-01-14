# -*- coding: utf-8 -*-
"""
Serviços de notificação para cadastros de usuários demo
Envia alertas por email e WhatsApp quando alguém demonstra interesse
"""

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def notificar_cadastro_demo_por_email(nome_completo, email, telefone, ip_address=None):
    """
    Envia notificação por email quando um usuário demo se cadastra

    Args:
        nome_completo: Nome completo do usuário
        email: Email do usuário
        telefone: Telefone do usuário (opcional)
        ip_address: Endereço IP do usuário (opcional)
    """
    try:
        # Configurações
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@monpec.com.br')
        subject = '[MONPEC] Novo Lead - Usuário Demo Cadastrado'

        # Contexto para o template
        context = {
            'nome_completo': nome_completo,
            'email': email,
            'telefone': telefone or 'Não informado',
            'ip_address': ip_address or 'Não identificado',
            'data_cadastro': timezone.now(),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        # Renderizar template HTML
        html_message = render_to_string('gestao_rural/emails/notificacao_demo.html', context)

        # Versão texto puro
        text_message = f"""
Novo lead de demonstração cadastrado!

Nome: {nome_completo}
Email: {email}
Telefone: {telefone or 'Não informado'}
IP: {ip_address or 'Não identificado'}
Data: {context['data_cadastro']}

Acesse o admin para ver todos os leads: {context['site_url']}/admin/
        """.strip()

        # Enviar email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br'),
            recipient_list=[admin_email],
            fail_silently=True
        )

        logger.info(f'[NOTIFICACAO_DEMO] Email enviado para {admin_email} sobre lead: {email}')
        return True

    except Exception as e:
        logger.error(f'[NOTIFICACAO_DEMO] Erro ao enviar email: {e}')
        return False


def notificar_cadastro_demo_por_whatsapp(nome_completo, email, telefone, ip_address=None):
    """
    Envia notificação por WhatsApp quando um usuário demo se cadastra

    Args:
        nome_completo: Nome completo do usuário
        email: Email do usuário
        telefone: Telefone do usuário (opcional)
        ip_address: Endereço IP do usuário (opcional)
    """
    try:
        # Verificar se WhatsApp está configurado
        whatsapp_token = getattr(settings, 'WHATSAPP_WEBHOOK_TOKEN', None)
        admin_whatsapp = getattr(settings, 'ADMIN_WHATSAPP', None)

        if not whatsapp_token or not admin_whatsapp:
            logger.info('[NOTIFICACAO_DEMO] WhatsApp não configurado, pulando notificação')
            return False

        # Importar serviço WhatsApp (se existir)
        try:
            from .services_whatsapp import enviar_mensagem_whatsapp
        except ImportError:
            logger.warning('[NOTIFICACAO_DEMO] Serviço WhatsApp não disponível')
            return False

        # Criar mensagem
        mensagem = f"""
🚀 *NOVO LEAD - MONPEC*

Nome: {nome_completo}
Email: {email}
Telefone: {telefone or 'Não informado'}
IP: {ip_address or 'Não identificado'}
Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}

Demonstrou interesse no sistema! 💪
        """.strip()

        # Enviar mensagem
        sucesso = enviar_mensagem_whatsapp(admin_whatsapp, mensagem)

        if sucesso:
            logger.info(f'[NOTIFICACAO_DEMO] WhatsApp enviado para {admin_whatsapp} sobre lead: {email}')
        else:
            logger.warning(f'[NOTIFICACAO_DEMO] Falha ao enviar WhatsApp para {admin_whatsapp}')

        return sucesso

    except Exception as e:
        logger.error(f'[NOTIFICACAO_DEMO] Erro ao enviar WhatsApp: {e}')
        return False


def notificar_cadastro_demo(nome_completo, email, telefone=None, ip_address=None):
    """
    Função principal para notificar cadastros de usuários demo
    Envia notificações por email e WhatsApp (se configurado)

    Args:
        nome_completo: Nome completo do usuário
        email: Email do usuário
        telefone: Telefone do usuário (opcional)
        ip_address: Endereço IP do usuário (opcional)
    """
    logger.info(f'[NOTIFICACAO_DEMO] Iniciando notificações para lead: {email}')

    # Enviar email (sempre)
    email_enviado = notificar_cadastro_demo_por_email(
        nome_completo=nome_completo,
        email=email,
        telefone=telefone,
        ip_address=ip_address
    )

    # Enviar WhatsApp (se configurado)
    whatsapp_enviado = notificar_cadastro_demo_por_whatsapp(
        nome_completo=nome_completo,
        email=email,
        telefone=telefone,
        ip_address=ip_address
    )

    # Log do resultado
    if email_enviado or whatsapp_enviado:
        logger.info(f'[NOTIFICACAO_DEMO] Notificações enviadas com sucesso para lead: {email}')
        return True
    else:
        logger.warning(f'[NOTIFICACAO_DEMO] Falha em todas as notificações para lead: {email}')
        return False


# Função para obter estatísticas de leads demo
def obter_estatisticas_leads_demo():
    """
    Retorna estatísticas sobre leads de usuários demo

    Returns:
        dict: Estatísticas dos leads
    """
    try:
        from django.contrib.auth.models import User
        from gestao_rural.models_auditoria import UsuarioAtivo

        # Contar usuários demo
        usuarios_demo = User.objects.filter(
            # Usuários que não são admin e não têm assinatura ativa
        ).exclude(username='admin').exclude(is_superuser=True)

        # Filtrar apenas usuários que são demo (têm UsuarioAtivo)
        usuarios_demo_ids = UsuarioAtivo.objects.values_list('usuario_id', flat=True)
        usuarios_demo = usuarios_demo.filter(id__in=usuarios_demo_ids)

        total_leads = usuarios_demo.count()

        # Leads recentes (últimos 30 dias)
        from django.utils import timezone
        from datetime import timedelta

        data_limite = timezone.now() - timedelta(days=30)
        leads_recentes = usuarios_demo.filter(date_joined__gte=data_limite).count()

        return {
            'total_leads': total_leads,
            'leads_recentes': leads_recentes,
            'leads_antigos': total_leads - leads_recentes,
            'data_atualizacao': timezone.now()
        }

    except Exception as e:
        logger.error(f'[ESTATISTICAS_DEMO] Erro ao obter estatísticas: {e}')
        return {
            'total_leads': 0,
            'leads_recentes': 0,
            'leads_antigos': 0,
            'erro': str(e)
        }