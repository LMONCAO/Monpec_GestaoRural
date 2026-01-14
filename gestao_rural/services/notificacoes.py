import logging
from typing import Iterable

from django.conf import settings  # type: ignore
from django.core.mail import send_mail, EmailMultiAlternatives  # type: ignore
from django.urls import reverse  # type: ignore


logger = logging.getLogger(__name__)


def _remetente_padrao() -> str | None:
    if hasattr(settings, "DEFAULT_FROM_EMAIL") and settings.DEFAULT_FROM_EMAIL:
        return settings.DEFAULT_FROM_EMAIL
    if hasattr(settings, "EMAIL_HOST_USER") and settings.EMAIL_HOST_USER:
        return settings.EMAIL_HOST_USER
    return None


def enviar_notificacao_compra(assunto: str, mensagem: str, destinatarios: Iterable[str], html_message: str = None) -> bool:
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
        if html_message:
            msg = EmailMultiAlternatives(
                subject=assunto,
                body=mensagem,
                from_email=remetente,
                to=emails
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
        else:
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
    # Removido: STRIPE_ALERT_EMAILS - usando apenas Mercado Pago
    # Retornar lista vazia ou configurar emails do Mercado Pago se necessário
    return []
    return []


def notificar_evento_assinatura(assinatura, assunto: str, mensagem: str) -> bool:
    """Notifica o time interno sobre eventos críticos de assinatura (Mercado Pago)."""
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


def notificar_consultor_nova_assinatura(assinatura) -> bool:
    """
    Notifica o consultor sobre uma nova assinatura confirmada.

    Args:
        assinatura: Instância de AssinaturaCliente

    Returns:
        bool: True se a notificação foi enviada com sucesso, False caso contrário
    """
    from django.conf import settings

    # Verificar se há email do consultor configurado
    consultor_email = getattr(settings, 'CONSULTOR_EMAIL', None)
    if not consultor_email:
        logger.warning("Email do consultor não configurado para notificações de nova assinatura")
        return False

    # Dados da assinatura
    usuario = assinatura.usuario
    plano = assinatura.plano
    data_liberacao = assinatura.data_liberacao.strftime('%d/%m/%Y') if assinatura.data_liberacao else 'Não definida'

    assunto = f"NOVA ASSINATURA CONFIRMADA - {usuario.get_full_name() or usuario.username}"

    mensagem_texto = f"""
Olá Consultor,

Uma nova assinatura foi confirmada no sistema MONPEC!

DETALHES DA ASSINATURA:
- ID da Assinatura: {assinatura.id}
- Cliente: {usuario.get_full_name() or usuario.username}
- Email: {usuario.email}
- Telefone: {getattr(usuario, 'telefone', 'Não informado')}
- Plano: {plano.nome if plano else 'N/A'}
- Valor: R$ {plano.preco_mensal_referencia if plano else 'N/A'}
- Status: {assinatura.get_status_display()}
- Data de Liberação: {data_liberacao}

AÇÃO NECESSÁRIA:
- Entrar em contato com o cliente através do email {usuario.email}
- Agendar demonstração personalizada do sistema
- Orientar sobre o uso da plataforma
- Confirmar que tudo está funcionando

IMPORTANTE:
- O cliente já recebeu email automático com credenciais
- Sistema será liberado em {data_liberacao}
- Senha padrão: Monpec2025@

Atenciosamente,
Sistema MONPEC - Gestão Rural Inteligente
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
        .details {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #0d6efd;
            border-radius: 5px;
        }}
        .action-needed {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 20px;
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
        <h1>🔔 NOVA ASSINATURA CONFIRMADA</h1>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>

    <div class="content">
        <p>Olá <strong>Consultor</strong>,</p>

        <p>Uma nova assinatura foi confirmada no sistema MONPEC! 🎉</p>

        <div class="details">
            <h3>📋 Detalhes da Assinatura</h3>
            <p><strong>ID:</strong> {assinatura.id}</p>
            <p><strong>Cliente:</strong> {usuario.get_full_name() or usuario.username}</p>
            <p><strong>Email:</strong> {usuario.email}</p>
            <p><strong>Telefone:</strong> {getattr(usuario, 'telefone', 'Não informado')}</p>
            <p><strong>Plano:</strong> {plano.nome if plano else 'N/A'}</p>
            <p><strong>Valor:</strong> R$ {plano.preco_mensal_referencia if plano else 'N/A'}</p>
            <p><strong>Status:</strong> {assinatura.get_status_display()}</p>
            <p><strong>Data de Liberação:</strong> {data_liberacao}</p>
        </div>

        <div class="action-needed">
            <h3 style="color: #856404; margin-top: 0;">⚡ AÇÃO NECESSÁRIA</h3>
            <ul>
                <li>📧 Entrar em contato com o cliente através do email <strong>{usuario.email}</strong></li>
                <li>📅 Agendar demonstração personalizada do sistema</li>
                <li>📖 Orientar sobre o uso da plataforma</li>
                <li>✅ Confirmar que tudo está funcionando</li>
            </ul>
        </div>

        <div class="details">
            <h3>🔑 Informações Importantes</h3>
            <ul>
                <li>O cliente já recebeu email automático com credenciais</li>
                <li>Sistema será liberado em <strong>{data_liberacao}</strong></li>
                <li>Senha padrão: <code>Monpec2025@</code></li>
                <li>Email de boas-vindas já foi enviado automaticamente</li>
            </ul>
        </div>

        <p>Atenciosamente,<br>
        <strong>Sistema MONPEC - Gestão Rural Inteligente</strong></p>
    </div>

    <div class="footer">
        <p>Este é um email automático do sistema. Não responda diretamente.</p>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
</body>
</html>
"""

    remetente = _remetente_padrao()
    try:
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=mensagem_texto,
            from_email=remetente,
            to=[consultor_email]
        )
        msg.attach_alternative(mensagem_html, "text/html")
        msg.send(fail_silently=False)

        logger.info("Notificação de nova assinatura enviada para consultor: %s (assinatura ID: %s)",
                   consultor_email, assinatura.id)
        return True
    except Exception as e:
        logger.exception("Falha ao enviar notificação de nova assinatura para consultor %s: %s",
                        consultor_email, str(e))
        return False


def enviar_convite_cotacao(convite) -> bool:
    """
    Envia e-mail de convite de cotação para o fornecedor.
    
    Args:
        convite: Instância de ConviteCotacaoFornecedor
        
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    if not convite.email_destinatario:
        logger.warning("Convite %s sem email destinatário", convite.id)
        return False
    
    # Garantir que o token existe
    if not convite.token:
        logger.warning("Convite %s sem token, gerando token...", convite.id)
        convite.save()  # Isso vai gerar o token no save()
    
    try:
        # Gerar URL completa do link de resposta
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        if not site_url.startswith('http'):
            site_url = f'http://{site_url}'
        
        link_resposta = f"{site_url}{reverse('cotacao_fornecedor_responder_token', args=[convite.token])}"
        
        logger.info("Link de resposta gerado: %s (token: %s)", link_resposta, convite.token)
        
        # Dados do convite
        fornecedor_nome = convite.fornecedor.nome
        requisicao_numero = convite.requisicao.numero
        requisicao_titulo = convite.requisicao.titulo
        data_expiracao = convite.data_expiracao.strftime('%d/%m/%Y às %H:%M') if convite.data_expiracao else 'Não informada'
        propriedade = convite.requisicao.propriedade
        propriedade_nome = propriedade.nome_propriedade
        
        # Dados do produtor rural
        produtor = propriedade.produtor
        produtor_nome = produtor.nome
        produtor_telefone = produtor.telefone or produtor.email or 'Não informado'
        produtor_email = produtor.email or 'Não informado'
        produtor_cpf_cnpj = produtor.cpf_cnpj or 'Não informado'
        
        # Forma de pagamento (da requisição ou padrão)
        forma_pagamento = 'A combinar'  # Pode ser melhorado com campo na requisição
        if hasattr(convite.requisicao, 'observacoes') and convite.requisicao.observacoes:
            # Tentar extrair forma de pagamento das observações se mencionado
            obs_lower = convite.requisicao.observacoes.lower()
            if 'pagamento' in obs_lower or 'pagto' in obs_lower:
                forma_pagamento = 'Ver observações da requisição'
        
        # Itens da requisição para o fornecedor saber o que cotar
        itens_requisicao = list(convite.requisicao.itens.all()[:10])  # Limitar a 10 itens no email
        
        # Assunto do email
        assunto = f'Convite para Cotação - Requisição {requisicao_numero} - {propriedade_nome}'
        
        # Lista de itens para o email
        lista_itens = ""
        total_itens = convite.requisicao.itens.count()
        for idx, item in enumerate(itens_requisicao, 1):
            lista_itens += f"\n{idx}. {item.descricao}"
            if item.quantidade:
                lista_itens += f" - Quantidade: {item.quantidade}"
            if item.unidade_medida:
                lista_itens += f" {item.get_unidade_medida_display()}"
            if item.observacoes:
                lista_itens += f" ({item.observacoes})"
        
        if total_itens > 10:
            lista_itens += f"\n\n... e mais {total_itens - 10} item(ns). Veja todos no portal."
        
        # Corpo do email em texto plano
        mensagem_texto = f"""
Olá {fornecedor_nome},

Você recebeu um convite para fornecer uma cotação através do sistema MONPEC - Gestão Rural Inteligente.

DETALHES DA REQUISIÇÃO:
- Número: {requisicao_numero}
- Título: {requisicao_titulo}
- Propriedade: {propriedade_nome}
- Data de Expiração: {data_expiracao}

DADOS DO PRODUTOR RURAL:
- Nome: {produtor_nome}
- CPF/CNPJ: {produtor_cpf_cnpj}
- Telefone: {produtor_telefone}
- E-mail: {produtor_email}

FORMA DE PAGAMENTO:
{forma_pagamento}

ITENS SOLICITADOS:
{lista_itens if lista_itens else "Ver detalhes no portal"}

Para acessar o portal e fornecer sua cotação, clique no link abaixo:

🔗 LINK PARA RESPONDER A COTAÇÃO:
{link_resposta}

OU copie e cole o link acima no seu navegador.

IMPORTANTE:
- Este link é único e seguro. Não compartilhe com terceiros.
- Você poderá preencher os preços dos itens e anexar sua proposta diretamente pelo portal.
- Após responder, sua cotação ficará disponível para análise.

Se você não deseja fornecer uma cotação para esta requisição, pode ignorar este email.

Atenciosamente,
{produtor_nome}
{propriedade_nome}
Equipe MONPEC - Gestão Rural Inteligente
"""
        
        # Corpo do email em HTML
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
            background-color: #0d6efd;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f8f9fa;
            padding: 30px;
            border: 1px solid #dee2e6;
        }}
        .details {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #0d6efd;
        }}
        .button {{
            display: inline-block;
            background-color: #0d6efd;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .button:hover {{
            background-color: #0b5ed7;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Gestão Rural Inteligente</h1>
        <p>Convite para Cotação</p>
    </div>
    
    <div class="content">
        <p>Olá <strong>{fornecedor_nome}</strong>,</p>
        
        <p>Você recebeu um convite para fornecer uma cotação através do sistema MONPEC - Gestão Rural Inteligente.</p>
        
        <div class="details">
            <h3>Detalhes da Requisição</h3>
            <p><strong>Número:</strong> {requisicao_numero}</p>
            <p><strong>Título:</strong> {requisicao_titulo}</p>
            <p><strong>Propriedade:</strong> {propriedade_nome}</p>
            <p><strong>Data de Expiração:</strong> {data_expiracao}</p>
        </div>
        
        <div class="details">
            <h3>Dados do Produtor Rural</h3>
            <p><strong>Nome:</strong> {produtor_nome}</p>
            <p><strong>CPF/CNPJ:</strong> {produtor_cpf_cnpj}</p>
            <p><strong>Telefone:</strong> {produtor_telefone}</p>
            <p><strong>E-mail:</strong> {produtor_email}</p>
        </div>
        
        <div class="details">
            <h3>Forma de Pagamento</h3>
            <p>{forma_pagamento}</p>
        </div>
        
        <div class="details">
            <h3>Itens Solicitados</h3>
            <ul>
                {"".join([f"<li><strong>{item.descricao}</strong>" + (f" - Quantidade: {item.quantidade}" if item.quantidade else "") + (f" {item.get_unidade_medida_display()}" if item.unidade_medida else "") + (f"<br><small>{item.observacoes}</small>" if item.observacoes else "") + "</li>" for item in itens_requisicao])}
                {f"<li><em>... e mais {total_itens - 10} item(ns). Veja todos no portal.</em></li>" if total_itens > 10 else ""}
            </ul>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_resposta}" class="button" style="font-size: 18px; padding: 15px 40px;">
                🔗 ACESSAR PORTAL DE COTAÇÃO
            </a>
        </div>
        
        <div class="details" style="background-color: #e7f3ff; border-left: 4px solid #0d6efd;">
            <h3 style="color: #0d6efd; margin-top: 0;">📋 Link para Responder</h3>
            <p style="word-break: break-all; font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                <a href="{link_resposta}" style="color: #0d6efd; text-decoration: none;">{link_resposta}</a>
            </p>
            <p style="margin-bottom: 0; font-size: 14px; color: #666;">
                <strong>Copie este link</strong> e cole no seu navegador caso o botão acima não funcione.
            </p>
        </div>
        
        <div class="warning">
            <strong>⚠️ Importante:</strong>
            <ul>
                <li>Este link é único e seguro. Não compartilhe com terceiros.</li>
                <li>Você poderá preencher os preços dos itens e anexar sua proposta diretamente pelo portal.</li>
                <li>Após responder, sua cotação ficará disponível para análise.</li>
            </ul>
        </div>
        
        <p>Se você não deseja fornecer uma cotação para esta requisição, pode ignorar este email.</p>
        
        <p>Atenciosamente,<br>
        <strong>{produtor_nome}</strong><br>
        {propriedade_nome}<br>
        <strong>Equipe MONPEC - Gestão Rural Inteligente</strong></p>
    </div>
    
    <div class="footer">
        <p>Este é um email automático, por favor não responda.</p>
        <p>MONPEC - Gestão Rural Inteligente | {site_url}</p>
    </div>
</body>
</html>
"""
        
        remetente = _remetente_padrao()
        if not remetente:
            logger.error("Não há remetente configurado para envio de emails")
            return False
        
        # Criar mensagem com HTML
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=mensagem_texto,
            from_email=remetente,
            to=[convite.email_destinatario]
        )
        msg.attach_alternative(mensagem_html, "text/html")
        
        # Enviar email
        try:
            msg.send(fail_silently=False)
            logger.info("Email de convite enviado com sucesso para %s (convite ID: %s, token: %s)",
                       convite.email_destinatario, convite.id, convite.token)
            return True
        except Exception as e:
            logger.error("Erro ao enviar email de convite para %s (convite ID: %s): %s",
                        convite.email_destinatario, convite.id, str(e))
            raise
def verificar_renovacoes_pendentes() -> dict:
    """
    Verifica assinaturas que precisam de renovação e envia lembretes.

    Returns:
        dict: Estatísticas da verificação
    """
    from gestao_rural.models import AssinaturaCliente
    from django.utils import timezone
    from datetime import timedelta
    import logging

    logger = logging.getLogger(__name__)

    # Buscar assinaturas ativas que vencem nos próximos 7 dias
    hoje = timezone.now().date()
    data_limite = hoje + timedelta(days=7)

    assinaturas_vencendo = AssinaturaCliente.objects.filter(
        status='ATIVA',
        current_period_end__date__lte=data_limite,
        current_period_end__date__gte=hoje
    ).select_related('usuario', 'plano')

    renovacoes_enviadas = 0
    erros = 0

    for assinatura in assinaturas_vencendo:
        try:
            # Verificar se já foi enviado lembrete (nos últimos 7 dias)
            if assinatura.metadata and assinatura.metadata.get('lembrete_renovacao_enviado'):
                ultimo_envio = assinatura.metadata.get('data_lembrete_renovacao')
                if ultimo_envio and (hoje - ultimo_envio).days < 7:
                    continue  # Já foi enviado lembrete recentemente

            # Enviar lembrete de renovação
            if enviar_lembrete_renovacao(assinatura):
                renovacoes_enviadas += 1

                # Marcar que foi enviado
                if not assinatura.metadata:
                    assinatura.metadata = {}
                assinatura.metadata['lembrete_renovacao_enviado'] = True
                assinatura.metadata['data_lembrete_renovacao'] = hoje
                assinatura.save(update_fields=['metadata', 'atualizado_em'])

        except Exception as e:
            logger.error(f"Erro ao processar renovação para assinatura {assinatura.id}: {e}")
            erros += 1

    return {
        'assinaturas_verificadas': len(assinaturas_vencendo),
        'renovacoes_enviadas': renovacoes_enviadas,
        'erros': erros
    }


def enviar_lembrete_renovacao(assinatura) -> bool:
    """
    Envia lembrete de renovação para uma assinatura.

    Args:
        assinatura: Instância de AssinaturaCliente

    Returns:
        bool: True se o lembrete foi enviado com sucesso
    """
    from django.conf import settings

    usuario = assinatura.usuario
    plano = assinatura.plano

    # Calcular dias até o vencimento
    from django.utils import timezone
    hoje = timezone.now().date()
    dias_restantes = (assinatura.current_period_end.date() - hoje).days

    assunto = f"Renovação de Assinatura MONPEC - {dias_restantes} dias restantes"

    mensagem_texto = f"""
Olá {usuario.get_full_name() or usuario.username},

Sua assinatura MONPEC vence em {dias_restantes} dias ({assinatura.current_period_end.strftime('%d/%m/%Y')})!

DETALHES DA RENOVAÇÃO:
- Plano Atual: {plano.nome if plano else 'N/A'}
- Valor: R$ {plano.preco_mensal_referencia if plano else 'N/A'}
- Vencimento: {assinatura.current_period_end.strftime('%d/%m/%Y')}

Para renovar sua assinatura automaticamente, acesse:
{settings.SITE_URL}/assinaturas/dashboard/

IMPORTANTE:
- A renovação é automática via Mercado Pago
- Você receberá confirmação por email
- Não há interrupção no serviço

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
            background: linear-gradient(135deg, #007bff 0%, #28a745 100%);
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
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
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
        <h1>🔄 Lembrete de Renovação</h1>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>

    <div class="content">
        <p>Olá <strong>{usuario.get_full_name() or usuario.username}</strong>,</p>

        <div class="warning">
            <h3 style="color: #856404; margin-top: 0;">⏰ SUA ASSINATURA VENCE EM {dias_restantes} DIAS</h3>
            <p style="margin-bottom: 0;"><strong>Data:</strong> {assinatura.current_period_end.strftime('%d/%m/%Y')}</p>
        </div>

        <h3>Detalhes da Renovação</h3>
        <ul>
            <li><strong>Plano Atual:</strong> {plano.nome if plano else 'N/A'}</li>
            <li><strong>Valor Mensal:</strong> R$ {plano.preco_mensal_referencia if plano else 'N/A'}</li>
            <li><strong>Próximo Vencimento:</strong> {assinatura.current_period_end.strftime('%d/%m/%Y')}</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{settings.SITE_URL}/assinaturas/dashboard/" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                RENOVAR AGORA
            </a>
        </div>

        <div class="warning">
            <strong>💡 Dica:</strong> Configure a renovação automática para nunca perder acesso ao sistema!
        </div>

        <p>Atenciosamente,<br>
        <strong>Equipe MONPEC - Gestão Rural Inteligente</strong></p>
    </div>

    <div class="footer">
        <p>Este é um email automático. Não responda diretamente.</p>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
</body>
</html>
"""

    remetente = _remetente_padrao()
    try:
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=mensagem_texto,
            from_email=remetente,
            to=[usuario.email]
        )
        msg.attach_alternative(mensagem_html, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Lembrete de renovação enviado para {usuario.email} (assinatura {assinatura.id})")
        return True
    except Exception as e:
        logger.exception(f"Falha ao enviar lembrete de renovação para {usuario.email}: {e}")
        return False


class WhatsAppService:
    """Serviço básico de integração com WhatsApp."""

    @staticmethod
    def gerar_link_mensagem(telefone: str, mensagem: str) -> str:
        """
        Gera link para enviar mensagem via WhatsApp.

        Args:
            telefone: Número de telefone (com ou sem +55)
            mensagem: Mensagem a ser enviada

        Returns:
            str: Link do WhatsApp
        """
        # Limpar telefone (remover espaços, traços, etc.)
        telefone = ''.join(filter(str.isdigit, telefone))

        # Adicionar código do país se não tiver
        if not telefone.startswith('55'):
            telefone = f'55{telefone}'

        # Codificar mensagem para URL
        from urllib.parse import quote
        mensagem_codificada = quote(mensagem)

        return f'https://wa.me/{telefone}?text={mensagem_codificada}'

    @staticmethod
    def enviar_notificacao_consultor(assinatura, telefone_consultor: str = None) -> str:
        """
        Gera link do WhatsApp para notificar consultor sobre nova assinatura.

        Args:
            assinatura: Instância de AssinaturaCliente
            telefone_consultor: Telefone do consultor (opcional)

        Returns:
            str: Link do WhatsApp ou mensagem de erro
        """
        if not telefone_consultor:
            return "Telefone do consultor não configurado"

        usuario = assinatura.usuario
        plano = assinatura.plano

        mensagem = f"""🔔 *NOVA ASSINATURA CONFIRMADA*

📋 *Dados do Cliente:*
• Nome: {usuario.get_full_name() or usuario.username}
• Email: {usuario.email}
• Plano: {plano.nome if plano else 'N/A'}
• Valor: R$ {plano.preco_mensal_referencia if plano else 'N/A'}

⚡ *AÇÃO NECESSÁRIA:*
• Entrar em contato via email
• Agendar demonstração
• Orientar sobre o sistema

_Link do sistema:_ {settings.SITE_URL}/admin/gestao_rural/assinaturacliente/{assinatura.id}/change/"""

        return WhatsAppService.gerar_link_mensagem(telefone_consultor, mensagem)

    @staticmethod
    def enviar_lembrete_cliente(assinatura, telefone_cliente: str = None) -> str:
        """
        Gera link do WhatsApp para lembrete ao cliente.

        Args:
            assinatura: Instância de AssinaturaCliente
            telefone_cliente: Telefone do cliente (opcional)

        Returns:
            str: Link do WhatsApp ou mensagem de erro
        """
        if not telefone_cliente and hasattr(assinatura.usuario, 'telefone'):
            telefone_cliente = assinatura.usuario.telefone

        if not telefone_cliente:
            return "Telefone do cliente não disponível"

        usuario = assinatura.usuario
        plano = assinatura.plano

        # Calcular dias até o vencimento
        from django.utils import timezone
        hoje = timezone.now().date()
        dias_restantes = (assinatura.current_period_end.date() - hoje).days

        mensagem = f"""⏰ *LEMBRETE DE RENOVAÇÃO*

Olá {usuario.get_full_name() or usuario.username}!

Sua assinatura MONPEC vence em *{dias_restantes} dias* ({assinatura.current_period_end.strftime('%d/%m/%Y')})

📊 *Seu Plano:*
• {plano.nome if plano else 'N/A'}
• R$ {plano.preco_mensal_referencia if plano else 'N/A'}/mês

🔄 *Renove agora e garanta continuidade:*
{settings.SITE_URL}/assinaturas/dashboard/

💡 *Dica:* Configure a renovação automática!"""

        return WhatsAppService.gerar_link_mensagem(telefone_cliente, mensagem)


class TemplateEmail:
    """Sistema básico de templates customizáveis para emails."""

    TEMPLATES = {
        'confirmacao_assinatura': {
            'assunto': 'Assinatura Confirmada - MONPEC - Pré-Lançamento',
            'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%); color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { background-color: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; }
        .credentials { background-color: white; padding: 20px; margin: 20px 0; border-left: 4px solid #0d6efd; border-radius: 5px; }
        .warning { background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Gestão Rural Inteligente</h1>
        <p>Assinatura Confirmada - Pré-Lançamento</p>
    </div>
    <div class="content">
        <p>Olá <strong>{nome_cliente}</strong>,</p>
        <p>Sua assinatura foi confirmada com sucesso!</p>

        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">📋 ASSINATURA DE PRÉ-LANÇAMENTO</h3>
            <p>O sistema MONPEC estará disponível a partir de <strong>{data_liberacao}</strong>.</p>
        </div>

        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">🔐 SUAS CREDENCIAIS DE ACESSO</h3>
            <p><strong>Email:</strong> {email_cliente}</p>
            <p><strong>Senha:</strong> {senha_padrao}</p>
        </div>

        <div class="warning">
            <strong>⚠️ IMPORTANTE:</strong>
            <ul>
                <li>Este é um sistema de pré-lançamento</li>
                <li>O acesso será liberado em <strong>{data_liberacao}</strong></li>
                <li>Um de nossos consultores entrará em contato em breve</li>
                <li>Guarde estas credenciais com segurança</li>
            </ul>
        </div>

        <p>Atenciosamente,<br><strong>Equipe MONPEC - Gestão Rural Inteligente</strong></p>
    </div>
    <div class="footer">
        <p>Este é um email automático, por favor não responda.</p>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
</body>
</html>
''',
            'texto': '''
Olá {nome_cliente},

Sua assinatura foi confirmada com sucesso!

ASSINATURA DE PRÉ-LANÇAMENTO
O sistema MONPEC estará disponível a partir de {data_liberacao}.

SUAS CREDENCIAIS DE ACESSO:
Email: {email_cliente}
Senha: {senha_padrao}

IMPORTANTE:
- Este é um sistema de pré-lançamento
- O acesso será liberado em {data_liberacao}
- Um de nossos consultores entrará em contato em breve
- Guarde estas credenciais com segurança

Atenciosamente,
Equipe MONPEC - Gestão Rural Inteligente
'''
        },

        'notificacao_consultor': {
            'assunto': 'NOVA ASSINATURA CONFIRMADA - {nome_cliente}',
            'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #0d6efd 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { background-color: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; }
        .action { background-color: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔔 NOVA ASSINATURA CONFIRMADA</h1>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
    <div class="content">
        <p>Olá <strong>Consultor</strong>,</p>
        <p>Uma nova assinatura foi confirmada no sistema!</p>

        <h3>📋 Detalhes da Assinatura</h3>
        <ul>
            <li><strong>ID:</strong> {assinatura_id}</li>
            <li><strong>Cliente:</strong> {nome_cliente}</li>
            <li><strong>Email:</strong> {email_cliente}</li>
            <li><strong>Plano:</strong> {plano_nome}</li>
            <li><strong>Valor:</strong> R$ {plano_valor}</li>
        </ul>

        <div class="action">
            <h4 style="color: #856404; margin-top: 0;">⚡ AÇÃO NECESSÁRIA</h4>
            <ul>
                <li>📧 Entrar em contato com o cliente através do email <strong>{email_cliente}</strong></li>
                <li>📅 Agendar demonstração personalizada</li>
                <li>📖 Orientar sobre o uso da plataforma</li>
            </ul>
        </div>

        <p>Atenciosamente,<br><strong>Sistema MONPEC</strong></p>
    </div>
    <div class="footer">
        <p>Este é um email automático do sistema.</p>
    </div>
</body>
</html>
''',
            'texto': '''
Olá Consultor,

Uma nova assinatura foi confirmada no sistema MONPEC!

DETALHES DA ASSINATURA:
- ID: {assinatura_id}
- Cliente: {nome_cliente}
- Email: {email_cliente}
- Plano: {plano_nome}
- Valor: R$ {plano_valor}

AÇÃO NECESSÁRIA:
- Entrar em contato com o cliente através do email {email_cliente}
- Agendar demonstração personalizada
- Orientar sobre o uso da plataforma

Atenciosamente,
Sistema MONPEC - Gestão Rural Inteligente
'''
        },

        'lembrete_renovacao': {
            'assunto': 'Renovação de Assinatura MONPEC - {dias_restantes} dias restantes',
            'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #007bff 0%, #28a745 100%); color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { background-color: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; }
        .warning { background-color: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center; }
        .footer { text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 Lembrete de Renovação</h1>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
    <div class="content">
        <p>Olá <strong>{nome_cliente}</strong>,</p>

        <div class="warning">
            <h3 style="color: #856404; margin-top: 0;">⏰ SUA ASSINATURA VENCE EM {dias_restantes} DIAS</h3>
            <p style="margin-bottom: 0;"><strong>Data:</strong> {data_vencimento}</p>
        </div>

        <h3>Detalhes da Renovação</h3>
        <ul>
            <li><strong>Plano Atual:</strong> {plano_nome}</li>
            <li><strong>Valor Mensal:</strong> R$ {plano_valor}</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_renovacao}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                RENOVAR AGORA
            </a>
        </div>

        <p>Atenciosamente,<br><strong>Equipe MONPEC</strong></p>
    </div>
    <div class="footer">
        <p>Este é um email automático.</p>
    </div>
</body>
</html>
''',
            'texto': '''
Olá {nome_cliente},

Sua assinatura MONPEC vence em {dias_restantes} dias ({data_vencimento})!

DETALHES DA RENOVAÇÃO:
- Plano Atual: {plano_nome}
- Valor: R$ {plano_valor}

Para renovar, acesse: {link_renovacao}

Atenciosamente,
Equipe MONPEC - Gestão Rural Inteligente
'''
        }
    }

    @classmethod
    def renderizar(cls, template_nome: str, contexto: dict) -> dict:
        """
        Renderiza um template de email com o contexto fornecido.

        Args:
            template_nome: Nome do template
            contexto: Dicionário com variáveis para substituir

        Returns:
            dict: {'assunto': str, 'html': str, 'texto': str}
        """
        if template_nome not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_nome}' não encontrado")

        template = cls.TEMPLATES[template_nome]

        assunto = template['assunto'].format(**contexto)
        html = template['html'].format(**contexto)
        texto = template['texto'].format(**contexto)

        return {
            'assunto': assunto,
            'html': html,
            'texto': texto
        }


def enviar_email_customizado(template_nome: str, contexto: dict, destinatarios: list) -> bool:
    """
    Envia email usando template customizável.

    Args:
        template_nome: Nome do template
        contexto: Variáveis para o template
        destinatarios: Lista de emails destinatários

    Returns:
        bool: True se enviado com sucesso
    """
    try:
        template_renderizado = TemplateEmail.renderizar(template_nome, contexto)

        remetente = _remetente_padrao()
        msg = EmailMultiAlternatives(
            subject=template_renderizado['assunto'],
            body=template_renderizado['texto'],
            from_email=remetente,
            to=destinatarios
        )
        msg.attach_alternative(template_renderizado['html'], "text/html")
        msg.send(fail_silently=False)

        return True
    except Exception as e:
        logger.exception(f"Erro ao enviar email customizado '{template_nome}': {e}")
        return False
        
        logger.info("Convite de cotação enviado para %s (convite ID: %s)", convite.email_destinatario, convite.id)
        return True
        
    except Exception as e:
        logger.exception(
            "Falha ao enviar convite de cotação para %s (convite ID: %s): %s",
            convite.email_destinatario,
            convite.id,
            str(e)
        )
        return False

