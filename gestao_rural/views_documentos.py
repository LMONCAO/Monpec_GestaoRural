# -*- coding: utf-8 -*-
"""
Views para gerenciamento de documentos da propriedade
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import EmailMessage
import urllib.parse

from .models import Propriedade, DocumentoPropriedade
from .decorators import obter_propriedade_com_permissao

logger = logging.getLogger(__name__)


@login_required
def documentos_lista(request, propriedade_id):
    """Lista todos os documentos da propriedade"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    documentos = DocumentoPropriedade.objects.filter(propriedade=propriedade).order_by('-data_upload')
    
    # Agrupar por tipo de documento
    documentos_por_tipo = {}
    for doc in documentos:
        tipo = doc.get_tipo_documento_display()
        if tipo not in documentos_por_tipo:
            documentos_por_tipo[tipo] = []
        documentos_por_tipo[tipo].append(doc)
    
    context = {
        'propriedade': propriedade,
        'documentos': documentos,
        'documentos_por_tipo': documentos_por_tipo,
    }
    
    return render(request, 'gestao_rural/documentos/lista.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def documento_upload(request, propriedade_id):
    """Upload de novo documento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        try:
            tipo_documento = request.POST.get('tipo_documento')
            nome_documento = request.POST.get('nome_documento', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            data_vencimento = request.POST.get('data_vencimento') or None
            observacoes = request.POST.get('observacoes', '').strip()
            arquivo = request.FILES.get('arquivo')
            
            # Validações
            if not tipo_documento:
                messages.error(request, 'Tipo de documento é obrigatório.')
                return redirect('documentos_lista', propriedade_id=propriedade_id)
            
            if not nome_documento:
                messages.error(request, 'Nome do documento é obrigatório.')
                return redirect('documentos_lista', propriedade_id=propriedade_id)
            
            if not arquivo:
                messages.error(request, 'Arquivo é obrigatório.')
                return redirect('documentos_lista', propriedade_id=propriedade_id)
            
            # Validar se é PDF
            if not arquivo.name.lower().endswith('.pdf'):
                messages.error(request, 'Apenas arquivos PDF são permitidos.')
                return redirect('documentos_lista', propriedade_id=propriedade_id)
            
            # Criar documento
            documento = DocumentoPropriedade.objects.create(
                propriedade=propriedade,
                tipo_documento=tipo_documento,
                nome_documento=nome_documento,
                descricao=descricao if descricao else None,
                data_vencimento=data_vencimento if data_vencimento else None,
                observacoes=observacoes if observacoes else None,
                arquivo=arquivo,
                criado_por=request.user
            )
            
            messages.success(request, f'Documento "{nome_documento}" enviado com sucesso!')
            logger.info(f'Documento {documento.id} criado por {request.user.username} para propriedade {propriedade_id}')
            
            return redirect('documentos_lista', propriedade_id=propriedade_id)
            
        except Exception as e:
            logger.error(f'Erro ao fazer upload de documento: {str(e)}', exc_info=True)
            messages.error(request, f'Erro ao fazer upload do documento: {str(e)}')
            return redirect('documentos_lista', propriedade_id=propriedade_id)
    
    # GET - mostrar formulário
    context = {
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/documentos/upload.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def documento_editar(request, propriedade_id, documento_id):
    """Editar documento existente"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    if request.method == 'POST':
        try:
            documento.tipo_documento = request.POST.get('tipo_documento')
            documento.nome_documento = request.POST.get('nome_documento', '').strip()
            documento.descricao = request.POST.get('descricao', '').strip() or None
            documento.data_vencimento = request.POST.get('data_vencimento') or None
            documento.observacoes = request.POST.get('observacoes', '').strip() or None
            
            # Se houver novo arquivo, substituir
            novo_arquivo = request.FILES.get('arquivo')
            if novo_arquivo:
                # Validar se é PDF
                if not novo_arquivo.name.lower().endswith('.pdf'):
                    messages.error(request, 'Apenas arquivos PDF são permitidos.')
                    return redirect('documento_editar', propriedade_id=propriedade_id, documento_id=documento_id)
                
                # Deletar arquivo antigo
                if documento.arquivo:
                    try:
                        documento.arquivo.delete(save=False)
                    except Exception as e:
                        logger.warning(f'Erro ao deletar arquivo antigo: {str(e)}')
                
                documento.arquivo = novo_arquivo
            
            documento.save()
            
            messages.success(request, f'Documento "{documento.nome_documento}" atualizado com sucesso!')
            logger.info(f'Documento {documento.id} editado por {request.user.username}')
            
            return redirect('documentos_lista', propriedade_id=propriedade_id)
            
        except Exception as e:
            logger.error(f'Erro ao editar documento: {str(e)}', exc_info=True)
            messages.error(request, f'Erro ao editar documento: {str(e)}')
            return redirect('documento_editar', propriedade_id=propriedade_id, documento_id=documento_id)
    
    # GET - mostrar formulário
    context = {
        'propriedade': propriedade,
        'documento': documento,
    }
    return render(request, 'gestao_rural/documentos/editar.html', context)


@login_required
@require_http_methods(["POST"])
def documento_excluir(request, propriedade_id, documento_id):
    """Excluir documento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    try:
        nome_documento = documento.nome_documento
        
        # Deletar arquivo físico
        if documento.arquivo:
            try:
                documento.arquivo.delete(save=False)
            except Exception as e:
                logger.warning(f'Erro ao deletar arquivo físico: {str(e)}')
        
        # Deletar registro
        documento.delete()
        
        messages.success(request, f'Documento "{nome_documento}" excluído com sucesso!')
        logger.info(f'Documento {documento_id} excluído por {request.user.username}')
        
    except Exception as e:
        logger.error(f'Erro ao excluir documento: {str(e)}', exc_info=True)
        messages.error(request, f'Erro ao excluir documento: {str(e)}')
    
    return redirect('documentos_lista', propriedade_id=propriedade_id)


@login_required
def documento_visualizar(request, propriedade_id, documento_id):
    """Visualizar documento PDF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    if not documento.arquivo:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('documentos_lista', propriedade_id=propriedade_id)
    
    try:
        response = FileResponse(
            documento.arquivo.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'inline; filename="{documento.arquivo.name}"'
        return response
    except Exception as e:
        logger.error(f'Erro ao visualizar documento: {str(e)}', exc_info=True)
        messages.error(request, f'Erro ao visualizar documento: {str(e)}')
        return redirect('documentos_lista', propriedade_id=propriedade_id)


@login_required
def documento_download(request, propriedade_id, documento_id):
    """Download do documento PDF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    if not documento.arquivo:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('documentos_lista', propriedade_id=propriedade_id)
    
    try:
        response = FileResponse(
            documento.arquivo.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{documento.arquivo.name}"'
        return response
    except Exception as e:
        logger.error(f'Erro ao baixar documento: {str(e)}', exc_info=True)
        messages.error(request, f'Erro ao baixar documento: {str(e)}')
        return redirect('documentos_lista', propriedade_id=propriedade_id)


@login_required
@require_http_methods(["POST"])
def documento_enviar_email(request, propriedade_id, documento_id):
    """Enviar documento por e-mail"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'sucesso': False, 'erro': 'E-mail não fornecido'}, status=400)
        
        # Validar formato do e-mail
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return JsonResponse({'sucesso': False, 'erro': 'E-mail inválido'}, status=400)
        
        if not documento.arquivo:
            return JsonResponse({'sucesso': False, 'erro': 'Arquivo não encontrado'}, status=404)
        
        # Preparar dados do e-mail
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #198754;">Documento - {documento.nome_documento}</h2>
                <p>Prezado(a),</p>
                <p>Segue em anexo o documento <strong>{documento.nome_documento}</strong> da propriedade <strong>{propriedade.nome_propriedade}</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Dados do Documento:</h3>
                    <p><strong>Tipo:</strong> {documento.get_tipo_documento_display()}</p>
                    <p><strong>Nome:</strong> {documento.nome_documento}</p>
                    {f'<p><strong>Data de Vencimento:</strong> {documento.data_vencimento.strftime("%d/%m/%Y")}</p>' if documento.data_vencimento else ''}
                    {f'<p><strong>Descrição:</strong> {documento.descricao}</p>' if documento.descricao else ''}
                    <p><strong>Propriedade:</strong> {propriedade.nome_propriedade}</p>
                </div>
                
                <p>O arquivo PDF está anexado a este e-mail.</p>
                <p>Em caso de dúvidas, entre em contato conosco.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    Este é um e-mail automático. Por favor, não responda diretamente a esta mensagem.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Criar mensagem de e-mail
        email_msg = EmailMessage(
            subject=f'{documento.nome_documento} - {propriedade.nome_propriedade}',
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@monpec.com.br',
            to=[email],
        )
        email_msg.content_subtype = "html"
        
        # Anexar PDF
        try:
            email_msg.attach_file(documento.arquivo.path, mimetype='application/pdf')
        except Exception as e:
            logger.warning(f'Erro ao anexar PDF ao e-mail: {str(e)}')
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro ao anexar arquivo: {str(e)}'
            }, status=500)
        
        # Enviar e-mail
        try:
            email_msg.send()
            logger.info(f'Documento {documento.id} enviado por e-mail para {email}')
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Documento enviado para {email} com sucesso!'
            })
        except Exception as e:
            logger.error(f'Erro ao enviar e-mail: {str(e)}', exc_info=True)
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro ao enviar e-mail: {str(e)}. Verifique as configurações de e-mail do servidor.'
            }, status=500)
    except Exception as e:
        logger.error(f'Erro ao enviar documento por e-mail: {str(e)}', exc_info=True)
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def documento_enviar_whatsapp(request, propriedade_id, documento_id):
    """Enviar documento por WhatsApp"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    documento = get_object_or_404(DocumentoPropriedade, id=documento_id, propriedade=propriedade)
    
    try:
        data = json.loads(request.body)
        telefone = data.get('telefone')
        
        if not telefone:
            return JsonResponse({'sucesso': False, 'erro': 'Telefone não fornecido'}, status=400)
        
        # Limpar telefone (remover caracteres não numéricos)
        telefone = ''.join(filter(str.isdigit, telefone))
        
        # Validar telefone (deve ter pelo menos 10 dígitos)
        if len(telefone) < 10:
            return JsonResponse({'sucesso': False, 'erro': 'Telefone inválido. Deve conter pelo menos 10 dígitos.'}, status=400)
        
        if not documento.arquivo:
            return JsonResponse({'sucesso': False, 'erro': 'Arquivo não encontrado'}, status=404)
        
        # Preparar mensagem para WhatsApp
        mensagem = f"""*{documento.nome_documento}*

Olá!

Segue o documento *{documento.nome_documento}* da propriedade *{propriedade.nome_propriedade}*.

*Dados do Documento:*
• Tipo: {documento.get_tipo_documento_display()}
• Nome: {documento.nome_documento}
{f'• Data de Vencimento: {documento.data_vencimento.strftime("%d/%m/%Y")}' if documento.data_vencimento else ''}
{f'• Descrição: {documento.descricao}' if documento.descricao else ''}

O arquivo PDF será enviado em seguida.

_Propriedade: {propriedade.nome_propriedade}_"""
        
        # Codificar mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem)
        
        # Verificar se há API do WhatsApp configurada
        whatsapp_api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        whatsapp_api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        whatsapp_api_instance = getattr(settings, 'WHATSAPP_API_INSTANCE', None)
        
        if whatsapp_api_url and whatsapp_api_token:
            # Enviar via API do WhatsApp
            try:
                try:
                    import requests
                except ImportError:
                    logger.warning('Biblioteca requests não instalada.')
                    raise Exception('Biblioteca requests não está instalada.')
                
                # Preparar dados para envio
                payload = {
                    'number': telefone,
                    'message': mensagem,
                    'token': whatsapp_api_token
                }
                
                if whatsapp_api_instance:
                    payload['instance'] = whatsapp_api_instance
                
                # Enviar mensagem de texto
                response = requests.post(
                    f'{whatsapp_api_url}/send-message',
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Tentar enviar arquivo PDF
                    if documento.arquivo and documento.arquivo.name:
                        try:
                            with open(documento.arquivo.path, 'rb') as pdf_file:
                                files = {'file': (f'{documento.nome_documento}.pdf', pdf_file, 'application/pdf')}
                                data = {
                                    'number': telefone,
                                    'token': whatsapp_api_token
                                }
                                if whatsapp_api_instance:
                                    data['instance'] = whatsapp_api_instance
                                
                                file_response = requests.post(
                                    f'{whatsapp_api_url}/send-file',
                                    files=files,
                                    data=data,
                                    timeout=30
                                )
                                if file_response.status_code == 200:
                                    logger.info(f'Documento {documento.id} enviado via WhatsApp API para {telefone}')
                                    return JsonResponse({
                                        'sucesso': True,
                                        'mensagem': f'Documento enviado via WhatsApp para {telefone} com sucesso!'
                                    })
                        except Exception as e:
                            logger.warning(f'Erro ao enviar PDF via WhatsApp API: {str(e)}')
                    
                    return JsonResponse({
                        'sucesso': True,
                        'mensagem': f'Mensagem enviada via WhatsApp para {telefone}. O arquivo precisa ser anexado manualmente.'
                    })
                else:
                    logger.warning(f'Erro na API do WhatsApp: {response.status_code} - {response.text}')
                    raise Exception('API do WhatsApp não disponível')
                    
            except Exception as e:
                logger.warning(f'Erro ao usar API do WhatsApp, usando link do WhatsApp Web: {str(e)}')
        
        # Opção 2: Link do WhatsApp Web (fallback)
        whatsapp_url = f'https://wa.me/{telefone}?text={mensagem_encoded}'
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Link do WhatsApp gerado para {telefone}. Clique para abrir o WhatsApp Web.',
            'whatsapp_url': whatsapp_url,
            'documento': {
                'nome': documento.nome_documento,
                'tipo': documento.get_tipo_documento_display(),
            },
            'tem_pdf': bool(documento.arquivo and documento.arquivo.name),
            'observacao': 'Se o arquivo PDF estiver disponível, você precisará anexá-lo manualmente no WhatsApp.'
        })
    except Exception as e:
        logger.error(f'Erro ao enviar documento por WhatsApp: {str(e)}', exc_info=True)
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)

