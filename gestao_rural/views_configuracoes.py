# -*- coding: utf-8 -*-
"""
Views de Configurações por Módulo
Sistema centralizado de cadastros/configurações para cada módulo do sistema.

Cada módulo tem sua própria página de configurações que agrupa todos os cadastros
necessários para o funcionamento correto do módulo.
"""

import json
import logging
from typing import Dict, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError, PermissionDenied
from django.conf import settings

from .decorators import obter_propriedade_com_permissao
from .models import Propriedade
from .constants_configuracoes import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MAX_PAGE_SIZE
from .services_configuracoes import ConfiguracoesService

logger = logging.getLogger(__name__)

# Importar estrutura de configurações
from .views_configuracoes_data import CONFIGURACOES_MODULOS


@login_required
@csrf_protect
def configuracoes_modulo(request, propriedade_id, modulo):
    """
    Página centralizada de configurações para um módulo específico.
    
    Agrupa todos os cadastros necessários do módulo em uma única página
    com sistema de abas para organização.
    
    Args:
        request: HttpRequest do Django
        propriedade_id: ID da propriedade
        modulo: Nome do módulo (ex: 'financeiro', 'compras', etc.)
    
    Returns:
        HttpResponse renderizada com template de configurações
    """
    try:
        propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        
        # Verificar se o módulo existe
        if modulo not in CONFIGURACOES_MODULOS:
            logger.warning(f'Usuário {request.user.username} tentou acessar módulo inexistente: {modulo}')
            messages.error(request, f'Módulo "{modulo}" não encontrado.')
            return redirect('dashboard')
        
        config_modulo = CONFIGURACOES_MODULOS[modulo]
        
        # Carregar dados de cada cadastro
        cadastros_com_dados = []
        for cadastro in config_modulo['cadastros']:
            cadastro_info = cadastro.copy()
            
            # Tentar carregar contagem de registros
            try:
                modelo_class = ConfiguracoesService.carregar_modelo_classe(cadastro['modelo'])
                total = ConfiguracoesService.obter_total_registros(modelo_class, propriedade)
                cadastro_info['total_registros'] = total
            except (ValueError, Exception) as e:
                logger.warning(f'Erro ao carregar total de registros para {cadastro["modelo"]}: {str(e)}')
                cadastro_info['total_registros'] = None
            
            cadastros_com_dados.append(cadastro_info)
        
        context = {
            'propriedade': propriedade,
            'modulo': modulo,
            'config_modulo': config_modulo,
            'cadastros': cadastros_com_dados,
            'titulo': f'Configurações - {config_modulo["nome"]}',
        }
        
        return render(
            request,
            'gestao_rural/configuracoes_modulo.html',
            context
        )
    
    except Exception as e:
        logger.exception(f'Erro ao carregar configurações do módulo {modulo}')
        messages.error(request, 'Erro ao carregar configurações. Tente novamente.')
        return redirect('dashboard')


@login_required
@csrf_protect
def configuracoes_modulo_ajax(request, propriedade_id, modulo, cadastro_id):
    """
    Endpoint AJAX para carregar dados de um cadastro específico com paginação.
    
    Args:
        request: HttpRequest do Django
        propriedade_id: ID da propriedade
        modulo: Nome do módulo
        cadastro_id: ID do cadastro dentro do módulo
    
    Returns:
        JsonResponse com estrutura:
        {
            'success': bool,
            'registros': List[Dict],
            'total': int,
            'page': int,
            'pages': int,
            'has_next': bool,
            'has_prev': bool
        }
    """
    try:
        propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        
        if modulo not in CONFIGURACOES_MODULOS:
            return JsonResponse({'error': 'Módulo não encontrado'}, status=404)
        
        config_modulo = CONFIGURACOES_MODULOS[modulo]
        cadastro_config = None
        
        for cad in config_modulo['cadastros']:
            if cad['id'] == cadastro_id:
                cadastro_config = cad
                break
        
        if not cadastro_config:
            return JsonResponse({'error': 'Cadastro não encontrado'}, status=404)
        
        # Carregar modelo
        modelo_class = ConfiguracoesService.carregar_modelo_classe(cadastro_config['modelo'])
        
        # Obter queryset otimizado
        queryset = ConfiguracoesService.obter_queryset(modelo_class, propriedade)
        
        # Paginação
        page = int(request.GET.get('page', DEFAULT_PAGE))
        per_page = min(int(request.GET.get('per_page', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
        
        paginator = Paginator(queryset, per_page)
        
        try:
            page_obj = paginator.get_page(page)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.get_page(1)
        
        # Serializar registros
        registros = [
            ConfiguracoesService.serializar_registro(obj) 
            for obj in page_obj
        ]
        
        return JsonResponse({
            'success': True,
            'registros': registros,
            'total': paginator.count,
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
            'per_page': per_page,
        })
    
    except ValueError as e:
        logger.warning(f'Erro de validação em configuracoes_modulo_ajax: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception(f'Erro ao carregar dados AJAX: {str(e)}')
        error_msg = f'Erro ao carregar dados: {str(e)}' if settings.DEBUG else 'Erro ao carregar dados'
        return JsonResponse({'error': error_msg}, status=500)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def configuracoes_modulo_editar_inline(request, propriedade_id, modulo, cadastro_id, registro_id):
    """
    Endpoint para edição inline de registros.
    
    Args:
        request: HttpRequest do Django
        propriedade_id: ID da propriedade
        modulo: Nome do módulo
        cadastro_id: ID do cadastro
        registro_id: ID do registro a editar
    
    Returns:
        JsonResponse com resultado da operação
    """
    try:
        propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        
        if modulo not in CONFIGURACOES_MODULOS:
            return JsonResponse({'error': 'Módulo não encontrado'}, status=404)
        
        # Carregar dados do request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        
        novo_nome = data.get('nome', '').strip()
        
        if not novo_nome:
            return JsonResponse({'error': 'Nome não pode estar vazio'}, status=400)
        
        # Obter configuração do cadastro
        config_modulo = CONFIGURACOES_MODULOS[modulo]
        cadastro_config = None
        
        for cad in config_modulo['cadastros']:
            if cad['id'] == cadastro_id:
                cadastro_config = cad
                break
        
        if not cadastro_config:
            return JsonResponse({'error': 'Cadastro não encontrado'}, status=404)
        
        # Carregar modelo
        modelo_class = ConfiguracoesService.carregar_modelo_classe(cadastro_config['modelo'])
        
        # Verificar permissão
        if not ConfiguracoesService.validar_permissao_edicao(request.user, propriedade, modelo_class):
            logger.warning(
                f'Usuário {request.user.username} tentou editar sem permissão: '
                f'{cadastro_config["modelo"]} #{registro_id}'
            )
            return JsonResponse({'error': 'Sem permissão para editar este registro'}, status=403)
        
        # Buscar registro
        if hasattr(modelo_class, 'propriedade'):
            registro = get_object_or_404(modelo_class, id=registro_id, propriedade=propriedade)
        else:
            registro = get_object_or_404(modelo_class, id=registro_id)
        
        # Atualizar nome (campo mais comum)
        if hasattr(registro, 'nome'):
            registro.nome = novo_nome
            registro.save(update_fields=['nome'])
            
            # Invalidar cache
            ConfiguracoesService.invalidar_cache_total(modelo_class, propriedade)
            
            logger.info(
                f'Usuário {request.user.username} editou {cadastro_config["modelo"]} '
                f'#{registro_id} da propriedade {propriedade_id}'
            )
            
            return JsonResponse({
                'success': True, 
                'nome': novo_nome,
                'id': registro.id
            })
        else:
            return JsonResponse({'error': 'Modelo não suporta edição inline'}, status=400)
    
    except ValueError as e:
        logger.warning(f'Erro de validação em editar_inline: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except ValidationError as e:
        logger.warning(f'Erro de validação Django: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception(f'Erro ao editar registro inline: {str(e)}')
        error_msg = f'Erro ao salvar: {str(e)}' if settings.DEBUG else 'Erro ao salvar'
        return JsonResponse({'error': error_msg}, status=500)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def configuracoes_modulo_excluir(request, propriedade_id, modulo, cadastro_id, registro_id):
    """
    Endpoint para exclusão de registros com validação de integridade.
    
    Args:
        request: HttpRequest do Django
        propriedade_id: ID da propriedade
        modulo: Nome do módulo
        cadastro_id: ID do cadastro
        registro_id: ID do registro a excluir
    
    Returns:
        JsonResponse com resultado da operação
    """
    try:
        propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        
        if modulo not in CONFIGURACOES_MODULOS:
            return JsonResponse({'error': 'Módulo não encontrado'}, status=404)
        
        # Obter configuração do cadastro
        config_modulo = CONFIGURACOES_MODULOS[modulo]
        cadastro_config = None
        
        for cad in config_modulo['cadastros']:
            if cad['id'] == cadastro_id:
                cadastro_config = cad
                break
        
        if not cadastro_config:
            return JsonResponse({'error': 'Cadastro não encontrado'}, status=404)
        
        # Carregar modelo
        modelo_class = ConfiguracoesService.carregar_modelo_classe(cadastro_config['modelo'])
        
        # Verificar permissão
        if not ConfiguracoesService.validar_permissao_edicao(request.user, propriedade, modelo_class):
            logger.warning(
                f'Usuário {request.user.username} tentou excluir sem permissão: '
                f'{cadastro_config["modelo"]} #{registro_id}'
            )
            return JsonResponse({'error': 'Sem permissão para excluir este registro'}, status=403)
        
        # Buscar registro
        if hasattr(modelo_class, 'propriedade'):
            registro = get_object_or_404(modelo_class, id=registro_id, propriedade=propriedade)
        else:
            registro = get_object_or_404(modelo_class, id=registro_id)
        
        # Verificar se registro está em uso (se método existir)
        if hasattr(registro, 'verificar_uso'):
            try:
                em_uso = registro.verificar_uso()
                if em_uso:
                    return JsonResponse({
                        'error': 'Registro está em uso e não pode ser excluído',
                        'detalhes': em_uso
                    }, status=400)
            except Exception as e:
                logger.warning(f'Erro ao verificar uso do registro: {str(e)}')
        
        # Excluir registro
        nome_registro = str(registro)
        registro.delete()
        
        # Invalidar cache
        ConfiguracoesService.invalidar_cache_total(modelo_class, propriedade)
        
        logger.info(
            f'Usuário {request.user.username} excluiu {cadastro_config["modelo"]} '
            f'#{registro_id} ({nome_registro}) da propriedade {propriedade_id}'
        )
        
        return JsonResponse({'success': True, 'mensagem': f'Registro "{nome_registro}" excluído com sucesso'})
    
    except ValueError as e:
        logger.warning(f'Erro de validação em excluir: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except IntegrityError as e:
        logger.warning(f'Erro de integridade ao excluir: {str(e)}')
        return JsonResponse({
            'error': 'Não é possível excluir este registro pois está sendo utilizado em outras partes do sistema'
        }, status=400)
    except Exception as e:
        logger.exception(f'Erro ao excluir registro: {str(e)}')
        error_msg = f'Erro ao excluir: {str(e)}' if settings.DEBUG else 'Erro ao excluir'
        return JsonResponse({'error': error_msg}, status=500)
