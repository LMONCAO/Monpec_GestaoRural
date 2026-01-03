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
        except Exception as e:
            logger.error("Erro ao enviar email de convite para %s (convite ID: %s): %s", 
                        convite.email_destinatario, convite.id, str(e))
            raise
        
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

