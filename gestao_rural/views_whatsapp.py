# -*- coding: utf-8 -*-
"""
Views para integração com WhatsApp - Registro de Nascimentos
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import MensagemWhatsApp, Propriedade
from .services.whatsapp_nascimentos import ProcessadorAudioNascimento
from .services.whatsapp_suplementacao import ProcessadorAudioSuplementacao

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_webhook(request):
    """
    Webhook para receber mensagens do WhatsApp
    
    Formato esperado (exemplo usando Twilio, Evolution API, ou similar):
    {
        "from": "5511999999999",
        "type": "audio",
        "mediaUrl": "https://...",
        "body": "texto transcrito (opcional)"
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        numero_whatsapp = data.get('from', '').replace('whatsapp:', '').strip()
        tipo_mensagem = data.get('type', 'text')
        conteudo_audio_url = data.get('mediaUrl') or data.get('audioUrl')
        conteudo_texto = data.get('body') or data.get('text') or data.get('transcription')
        
        # Detectar tipo de registro baseado no conteúdo
        tipo_registro = 'NASCIMENTO'  # Padrão
        if conteudo_texto:
            texto_lower = conteudo_texto.lower()
            if any(palavra in texto_lower for palavra in ['distribuí', 'distribuir', 'distribuindo', 'suplementação', 'suplemento', 'ração', 'sal mineral']):
                tipo_registro = 'SUPLEMENTACAO'
            elif any(palavra in texto_lower for palavra in ['nascimento', 'nasceu', 'bezerro', 'bezerra', 'vaca teve']):
                tipo_registro = 'NASCIMENTO'
        
        # Identificar propriedade pelo número (pode ser configurado)
        # Por enquanto, vamos tentar encontrar pela primeira propriedade do usuário
        propriedade = None
        if numero_whatsapp:
            # Aqui você pode implementar uma lógica para associar número a propriedade
            # Por exemplo, criar um modelo PropriedadeWhatsApp
            propriedade = Propriedade.objects.first()  # Placeholder
        
        # Criar registro da mensagem
        mensagem = MensagemWhatsApp.objects.create(
            numero_whatsapp=numero_whatsapp,
            tipo_mensagem=tipo_mensagem,
            tipo_registro=tipo_registro,
            conteudo_audio_url=conteudo_audio_url,
            conteudo_texto=conteudo_texto,
            propriedade=propriedade,
            status='PENDENTE'
        )
        
        # Se já temos texto transcrito, processar imediatamente
        if conteudo_texto:
            processar_mensagem(mensagem.id)
        
        return JsonResponse({
            'status': 'success',
            'message_id': mensagem.id,
            'message': 'Mensagem recebida e aguardando processamento'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook WhatsApp: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_processar_audio(request):
    """
    Endpoint para processar áudio transcrito manualmente
    Útil quando o áudio é enviado separadamente
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        mensagem_id = data.get('message_id')
        texto_transcrito = data.get('texto')
        
        if not mensagem_id or not texto_transcrito:
            return JsonResponse({
                'status': 'error',
                'message': 'message_id e texto são obrigatórios'
            }, status=400)
        
        mensagem = get_object_or_404(MensagemWhatsApp, id=mensagem_id)
        mensagem.conteudo_texto = texto_transcrito
        mensagem.save()
        
        resultado = processar_mensagem(mensagem_id)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao processar áudio: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def processar_mensagem(mensagem_id: int) -> dict:
    """
    Processa uma mensagem pendente e tenta registrar o nascimento
    
    Retorna dicionário com status e informações
    """
    mensagem = get_object_or_404(MensagemWhatsApp, id=mensagem_id)
    
    if mensagem.status != 'PENDENTE':
        return {
            'status': 'error',
            'message': f'Mensagem já foi processada (status: {mensagem.status})'
        }
    
    mensagem.status = 'PROCESSANDO'
    mensagem.save()
    
    try:
        # Escolher processador baseado no tipo de registro
        if mensagem.tipo_registro == 'SUPLEMENTACAO':
            processador = ProcessadorAudioSuplementacao()
        else:
            processador = ProcessadorAudioNascimento()
        
        if not mensagem.conteudo_texto:
            return {
                'status': 'error',
                'message': 'Texto transcrito não disponível'
            }
        
        # Extrair dados do texto
        dados = processador.processar_texto(mensagem.conteudo_texto)
        mensagem.dados_extraidos = dados
        mensagem.save()
        
        # Validar dados
        valido, erro = processador.validar_dados(dados, mensagem.propriedade)
        
        if not valido:
            mensagem.status = 'ERRO'
            mensagem.erro_processamento = erro
            mensagem.save()
            return {
                'status': 'error',
                'message': erro,
                'dados_extraidos': dados
            }
        
        # Registrar baseado no tipo
        if mensagem.tipo_registro == 'SUPLEMENTACAO':
            registro = processador.registrar_distribuicao(mensagem, dados)
            tipo_registro = 'Distribuição de Suplementação'
            registro_id = registro.id if registro else None
        else:
            registro = processador.registrar_nascimento(mensagem, dados)
            tipo_registro = 'Nascimento'
            registro_id = registro.id if registro else None
        
        if registro:
            mensagem.status = 'PROCESSADO'
            mensagem.data_processamento = timezone.now()
            mensagem.save()
            
            return {
                'status': 'success',
                'message': f'{tipo_registro} registrado com sucesso',
                'registro_id': registro_id,
                'tipo_registro': mensagem.tipo_registro,
                'dados_extraidos': dados
            }
        else:
            mensagem.status = 'ERRO'
            mensagem.erro_processamento = f'Erro ao criar registro de {tipo_registro.lower()}'
            mensagem.save()
            return {
                'status': 'error',
                'message': f'Erro ao criar registro de {tipo_registro.lower()}'
            }
            
    except Exception as e:
        mensagem.status = 'ERRO'
        mensagem.erro_processamento = str(e)
        mensagem.save()
        logger.error(f"Erro ao processar mensagem {mensagem_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@login_required
def whatsapp_mensagens_lista(request, propriedade_id):
    """Lista mensagens de WhatsApp recebidas para uma propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    mensagens = MensagemWhatsApp.objects.filter(
        propriedade=propriedade
    ).order_by('-data_recebimento')[:50]
    
    from django.template.response import TemplateResponse
    return TemplateResponse(request, 'gestao_rural/whatsapp_mensagens_lista.html', {
        'propriedade': propriedade,
        'mensagens': mensagens,
    })


@login_required
@require_http_methods(["POST"])
def whatsapp_reprocessar(request, mensagem_id):
    """Reprocessa uma mensagem que falhou"""
    mensagem = get_object_or_404(MensagemWhatsApp, id=mensagem_id)
    
    mensagem.status = 'PENDENTE'
    mensagem.erro_processamento = ''
    mensagem.save()
    
    resultado = processar_mensagem(mensagem_id)
    
    return JsonResponse(resultado)

