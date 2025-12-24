# -*- coding: utf-8 -*-
"""
Views para geração e download de arquivos fiscais (Sintegra, SPED)
"""

import logging
from datetime import datetime, date
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from gestao_rural.models import Propriedade
from gestao_rural.services.sintegra_service import gerar_arquivo_sintegra
from gestao_rural.services.sped_service import gerar_arquivo_sped

logger = logging.getLogger(__name__)


@login_required
def fiscal_dashboard(request, propriedade_id):
    """
    Dashboard para geração de arquivos fiscais
    """
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Verificar permissão
    if not request.user.has_perm('gestao_rural.view_propriedade', propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return HttpResponse('Sem permissão', status=403)
    
    # Obter ano atual
    ano_atual = datetime.now().year
    
    context = {
        'propriedade': propriedade,
        'ano_atual': ano_atual,
        'anos_disponiveis': range(ano_atual - 2, ano_atual + 1),
    }
    
    return render(request, 'gestao_rural/fiscal_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def download_sintegra(request, propriedade_id):
    """
    Gera e faz download do arquivo Sintegra
    """
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Verificar permissão
    if not request.user.has_perm('gestao_rural.view_propriedade', propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return HttpResponse('Sem permissão', status=403)
    
    if request.method == 'POST':
        # Processar formulário
        try:
            periodo_inicio_str = request.POST.get('periodo_inicio')
            periodo_fim_str = request.POST.get('periodo_fim')
            uf = request.POST.get('uf', propriedade.uf)
            
            if not periodo_inicio_str or not periodo_fim_str:
                messages.error(request, 'Período inicial e final são obrigatórios.')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            
            periodo_inicio = datetime.strptime(periodo_inicio_str, '%Y-%m-%d').date()
            periodo_fim = datetime.strptime(periodo_fim_str, '%Y-%m-%d').date()
            
            # Validar período
            if periodo_inicio > periodo_fim:
                messages.error(request, 'Data inicial não pode ser maior que data final.')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            
            # Gerar arquivo
            try:
                arquivo = gerar_arquivo_sintegra(
                    propriedade_id=propriedade.id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    uf=uf
                )
                
                # Preparar resposta
                response = HttpResponse(
                    arquivo,
                    content_type='text/plain; charset=iso-8859-1'
                )
                
                nome_arquivo = (
                    f"sintegra_{propriedade.uf}_{periodo_inicio.year}"
                    f"{periodo_inicio.month:02d}_{periodo_fim.month:02d}.txt"
                )
                
                response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
                
                messages.success(
                    request,
                    f'Arquivo Sintegra gerado com sucesso para o período '
                    f'{periodo_inicio.strftime("%d/%m/%Y")} a '
                    f'{periodo_fim.strftime("%d/%m/%Y")}.'
                )
                
                return response
                
            except ValueError as e:
                messages.error(request, f'Erro ao gerar arquivo: {str(e)}')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            except Exception as e:
                logger.error(f"Erro ao gerar arquivo Sintegra: {e}", exc_info=True)
                messages.error(
                    request,
                    'Erro ao gerar arquivo. Verifique os logs do sistema.'
                )
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
                
        except ValueError as e:
            messages.error(request, f'Data inválida: {str(e)}')
            return render(request, 'gestao_rural/fiscal_dashboard.html', {
                'propriedade': propriedade
            })
    
    # GET - mostrar formulário
    ano_atual = datetime.now().year
    periodo_inicio = date(ano_atual, 1, 1)
    periodo_fim = date(ano_atual, 12, 31)
    
    context = {
        'propriedade': propriedade,
        'periodo_inicio': periodo_inicio,
        'periodo_fim': periodo_fim,
        'uf': propriedade.uf,
    }
    
    return render(request, 'gestao_rural/fiscal_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def download_sped(request, propriedade_id):
    """
    Gera e faz download do arquivo SPED Fiscal
    """
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Verificar permissão
    if not request.user.has_perm('gestao_rural.view_propriedade', propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return HttpResponse('Sem permissão', status=403)
    
    if request.method == 'POST':
        try:
            periodo_inicio_str = request.POST.get('periodo_inicio')
            periodo_fim_str = request.POST.get('periodo_fim')
            
            if not periodo_inicio_str or not periodo_fim_str:
                messages.error(request, 'Período inicial e final são obrigatórios.')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            
            periodo_inicio = datetime.strptime(periodo_inicio_str, '%Y-%m-%d').date()
            periodo_fim = datetime.strptime(periodo_fim_str, '%Y-%m-%d').date()
            
            if periodo_inicio > periodo_fim:
                messages.error(request, 'Data inicial não pode ser maior que data final.')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            
            # Gerar arquivo
            try:
                arquivo = gerar_arquivo_sped(
                    propriedade_id=propriedade.id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim
                )
                
                # Preparar resposta
                response = HttpResponse(
                    arquivo,
                    content_type='text/plain; charset=iso-8859-1'
                )
                
                nome_arquivo = (
                    f"SPED_Fiscal_{propriedade.uf}_{periodo_inicio.year}"
                    f"{periodo_inicio.month:02d}_{periodo_fim.month:02d}.txt"
                )
                
                response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
                
                messages.success(
                    request,
                    f'Arquivo SPED gerado com sucesso para o período '
                    f'{periodo_inicio.strftime("%d/%m/%Y")} a '
                    f'{periodo_fim.strftime("%d/%m/%Y")}.'
                )
                
                return response
                
            except ValueError as e:
                messages.error(request, f'Erro ao gerar arquivo: {str(e)}')
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
            except Exception as e:
                logger.error(f"Erro ao gerar arquivo SPED: {e}", exc_info=True)
                messages.error(
                    request,
                    'Erro ao gerar arquivo. Verifique os logs do sistema.'
                )
                return render(request, 'gestao_rural/fiscal_dashboard.html', {
                    'propriedade': propriedade
                })
                
        except ValueError as e:
            messages.error(request, f'Data inválida: {str(e)}')
            return render(request, 'gestao_rural/fiscal_dashboard.html', {
                'propriedade': propriedade
            })
    
    # GET - redirecionar para dashboard
    return redirect('fiscal_dashboard', propriedade_id=propriedade.id)


@login_required
def validar_dados_fiscais(request, propriedade_id):
    """
    API para validar dados fiscais da propriedade
    """
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not request.user.has_perm('gestao_rural.view_propriedade', propriedade):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    from gestao_rural.services.sintegra_service import SintegraService
    
    service = SintegraService(propriedade)
    valido, erros = service.validar_dados_obrigatorios()
    
    return JsonResponse({
        'valido': valido,
        'erros': erros,
        'dados': {
            'cnpj_cpf': propriedade.produtor.cpf_cnpj or '',
            'inscricao_estadual': propriedade.inscricao_estadual or '',
            'municipio': propriedade.municipio or '',
            'uf': propriedade.uf or '',
        }
    })

