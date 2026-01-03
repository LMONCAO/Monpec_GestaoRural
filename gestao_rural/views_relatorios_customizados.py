# -*- coding: utf-8 -*-
"""
Views para Sistema de Relatórios Customizados
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import json

from .models import Propriedade
from .models_relatorios_customizados import RelatorioCustomizado, TemplateRelatorio
from .forms_relatorios_customizados import RelatorioCustomizadoForm, ExecutarRelatorioForm
from .gerador_relatorios_dinamico import GeradorRelatoriosDinamico


@login_required
def relatorios_customizados_lista(request, propriedade_id):
    """Lista todos os relatórios customizados da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Buscar relatórios do usuário ou compartilhados
    relatorios = RelatorioCustomizado.objects.filter(
        propriedade=propriedade,
        ativo=True
    ).filter(
        Q(usuario_criador=request.user) | Q(compartilhado=True)
    ).order_by('-data_atualizacao')
    
    # Buscar templates disponíveis
    templates = TemplateRelatorio.objects.filter(
        Q(modulo__in=[r.modulo for r in relatorios] if relatorios else []) | Q(publico=True),
        ativo=True
    )
    
    context = {
        'propriedade': propriedade,
        'relatorios': relatorios,
        'templates': templates,
    }
    
    return render(request, 'gestao_rural/relatorios_customizados_lista.html', context)


@login_required
def relatorio_customizado_criar(request, propriedade_id):
    """Cria um novo relatório customizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = RelatorioCustomizadoForm(request.POST)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.propriedade = propriedade
            relatorio.usuario_criador = request.user
            
            # Processar dados JSON
            if isinstance(request.POST.get('campos_selecionados'), str):
                relatorio.campos_selecionados = json.loads(request.POST.get('campos_selecionados', '[]'))
            if isinstance(request.POST.get('filtros'), str):
                relatorio.filtros = json.loads(request.POST.get('filtros', '{}'))
            if isinstance(request.POST.get('agrupamentos'), str):
                relatorio.agrupamentos = json.loads(request.POST.get('agrupamentos', '[]'))
            if isinstance(request.POST.get('ordenacao'), str):
                relatorio.ordenacao = json.loads(request.POST.get('ordenacao', '[]'))
            if isinstance(request.POST.get('formatacao'), str):
                relatorio.formatacao = json.loads(request.POST.get('formatacao', '{}'))
            
            relatorio.save()
            messages.success(request, f'Relatório "{relatorio.nome}" criado com sucesso!')
            return redirect('relatorio_customizado_editar', propriedade_id=propriedade.id, relatorio_id=relatorio.id)
    else:
        # Verificar se está criando a partir de um template
        template_id = request.GET.get('template_id')
        if template_id:
            template = get_object_or_404(TemplateRelatorio, id=template_id, ativo=True)
            config = template.configuracao
            initial = {
                'nome': f"{template.nome} (Cópia)",
                'modulo': template.modulo,
                'campos_selecionados': config.get('campos_selecionados', []),
                'filtros': config.get('filtros', {}),
                'agrupamentos': config.get('agrupamentos', []),
                'ordenacao': config.get('ordenacao', []),
                'formatacao': config.get('formatacao', {}),
                'template_personalizado': template.template_html,
            }
            form = RelatorioCustomizadoForm(initial=initial)
        else:
            form = RelatorioCustomizadoForm()
    
    # Obter campos disponíveis por módulo
    campos_disponiveis = _obter_campos_disponiveis()
    
    # Se veio de um template, serializar os dados iniciais
    campos_selecionados_json = '[]'
    filtros_json = '{}'
    agrupamentos_json = '[]'
    ordenacao_json = '[]'
    
    if 'template_id' in request.GET:
        template_id = request.GET.get('template_id')
        if template_id:
            try:
                template = TemplateRelatorio.objects.get(id=template_id, ativo=True)
                config = template.configuracao
                campos_selecionados_json = json.dumps(config.get('campos_selecionados', []))
                filtros_json = json.dumps(config.get('filtros', {}))
                agrupamentos_json = json.dumps(config.get('agrupamentos', []))
                ordenacao_json = json.dumps(config.get('ordenacao', []))
            except TemplateRelatorio.DoesNotExist:
                pass
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'campos_disponiveis': json.dumps(campos_disponiveis),
        'campos_selecionados_json': campos_selecionados_json,
        'filtros_json': filtros_json,
        'agrupamentos_json': agrupamentos_json,
        'ordenacao_json': ordenacao_json,
    }
    
    return render(request, 'gestao_rural/relatorio_customizado_criar.html', context)


@login_required
def relatorio_customizado_editar(request, propriedade_id, relatorio_id):
    """Edita um relatório customizado existente"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    relatorio = get_object_or_404(
        RelatorioCustomizado,
        id=relatorio_id,
        propriedade=propriedade,
        ativo=True
    )
    
    # Verificar permissão
    if relatorio.usuario_criador != request.user and not relatorio.compartilhado:
        messages.error(request, 'Você não tem permissão para editar este relatório.')
        return redirect('relatorios_customizados_lista', propriedade_id=propriedade.id)
    
    if request.method == 'POST':
        form = RelatorioCustomizadoForm(request.POST, instance=relatorio)
        if form.is_valid():
            relatorio = form.save(commit=False)
            
            # Processar dados JSON
            if isinstance(request.POST.get('campos_selecionados'), str):
                relatorio.campos_selecionados = json.loads(request.POST.get('campos_selecionados', '[]'))
            if isinstance(request.POST.get('filtros'), str):
                relatorio.filtros = json.loads(request.POST.get('filtros', '{}'))
            if isinstance(request.POST.get('agrupamentos'), str):
                relatorio.agrupamentos = json.loads(request.POST.get('agrupamentos', '[]'))
            if isinstance(request.POST.get('ordenacao'), str):
                relatorio.ordenacao = json.loads(request.POST.get('ordenacao', '[]'))
            if isinstance(request.POST.get('formatacao'), str):
                relatorio.formatacao = json.loads(request.POST.get('formatacao', '{}'))
            
            relatorio.save()
            messages.success(request, f'Relatório "{relatorio.nome}" atualizado com sucesso!')
            return redirect('relatorio_customizado_editar', propriedade_id=propriedade.id, relatorio_id=relatorio.id)
    else:
        form = RelatorioCustomizadoForm(instance=relatorio)
    
    # Obter campos disponíveis por módulo
    campos_disponiveis = _obter_campos_disponiveis()
    
    # Serializar campos selecionados e outros dados para o template
    campos_selecionados_json = json.dumps(relatorio.get_campos_selecionados_list() if relatorio else [])
    filtros_json = json.dumps(relatorio.get_filtros_dict() if relatorio else {})
    agrupamentos_json = json.dumps(relatorio.get_agrupamentos_list() if relatorio else [])
    ordenacao_json = json.dumps(relatorio.get_ordenacao_list() if relatorio else [])
    
    context = {
        'propriedade': propriedade,
        'relatorio': relatorio,
        'form': form,
        'campos_disponiveis': json.dumps(campos_disponiveis),
        'campos_selecionados_json': campos_selecionados_json,
        'filtros_json': filtros_json,
        'agrupamentos_json': agrupamentos_json,
        'ordenacao_json': ordenacao_json,
    }
    
    return render(request, 'gestao_rural/relatorio_customizado_editar.html', context)


@login_required
def relatorio_customizado_executar(request, propriedade_id, relatorio_id):
    """Executa um relatório customizado e exibe/exporta os resultados"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    relatorio = get_object_or_404(
        RelatorioCustomizado,
        id=relatorio_id,
        propriedade=propriedade,
        ativo=True
    )
    
    # Verificar permissão
    if relatorio.usuario_criador != request.user and not relatorio.compartilhado:
        messages.error(request, 'Você não tem permissão para executar este relatório.')
        return redirect('relatorios_customizados_lista', propriedade_id=propriedade.id)
    
    # Incrementar contador de execuções
    relatorio.incrementar_execucao()
    
    # Obter filtros adicionais do formulário
    form = ExecutarRelatorioForm(request.GET)
    filtros_adicionais = {}
    if form.is_valid():
        if form.cleaned_data.get('data_inicio'):
            filtros_adicionais['data_inicio'] = form.cleaned_data['data_inicio']
        if form.cleaned_data.get('data_fim'):
            filtros_adicionais['data_fim'] = form.cleaned_data['data_fim']
        formato = form.cleaned_data.get('formato', 'html')
    else:
        formato = request.GET.get('formato', 'html')
    
    # Gerar relatório
    gerador = GeradorRelatoriosDinamico()
    
    try:
        if formato == 'pdf':
            response = gerador.gerar_pdf(relatorio, propriedade, filtros_adicionais)
            return response
        elif formato == 'excel':
            response = gerador.gerar_excel(relatorio, propriedade, filtros_adicionais)
            return response
        else:  # HTML
            dados = gerador.gerar_dados(relatorio, propriedade, filtros_adicionais)
            context = {
                'propriedade': propriedade,
                'relatorio': relatorio,
                'dados': dados,
                'form': ExecutarRelatorioForm(request.GET),
            }
            return render(request, 'gestao_rural/relatorio_customizado_resultado.html', context)
    except Exception as e:
        messages.error(request, f'Erro ao gerar relatório: {str(e)}')
        return redirect('relatorio_customizado_editar', propriedade_id=propriedade.id, relatorio_id=relatorio.id)


@login_required
def relatorio_customizado_excluir(request, propriedade_id, relatorio_id):
    """Exclui (desativa) um relatório customizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    relatorio = get_object_or_404(
        RelatorioCustomizado,
        id=relatorio_id,
        propriedade=propriedade,
        usuario_criador=request.user
    )
    
    if request.method == 'POST':
        relatorio.ativo = False
        relatorio.save()
        messages.success(request, f'Relatório "{relatorio.nome}" excluído com sucesso!')
        return redirect('relatorios_customizados_lista', propriedade_id=propriedade.id)
    
    context = {
        'propriedade': propriedade,
        'relatorio': relatorio,
    }
    
    return render(request, 'gestao_rural/relatorio_customizado_excluir.html', context)


@login_required
def relatorio_customizado_duplicar(request, propriedade_id, relatorio_id):
    """Duplica um relatório customizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    relatorio_original = get_object_or_404(
        RelatorioCustomizado,
        id=relatorio_id,
        propriedade=propriedade,
        ativo=True
    )
    
    # Verificar permissão
    if relatorio_original.usuario_criador != request.user and not relatorio_original.compartilhado:
        messages.error(request, 'Você não tem permissão para duplicar este relatório.')
        return redirect('relatorios_customizados_lista', propriedade_id=propriedade.id)
    
    # Criar cópia
    relatorio_novo = RelatorioCustomizado.objects.create(
        nome=f"{relatorio_original.nome} (Cópia)",
        descricao=relatorio_original.descricao,
        propriedade=propriedade,
        usuario_criador=request.user,
        modulo=relatorio_original.modulo,
        tipo_exportacao=relatorio_original.tipo_exportacao,
        campos_selecionados=relatorio_original.campos_selecionados,
        filtros=relatorio_original.filtros,
        agrupamentos=relatorio_original.agrupamentos,
        ordenacao=relatorio_original.ordenacao,
        formatacao=relatorio_original.formatacao,
        template_personalizado=relatorio_original.template_personalizado,
        compartilhado=False,
        ativo=True
    )
    
    messages.success(request, f'Relatório duplicado com sucesso!')
    return redirect('relatorio_customizado_editar', propriedade_id=propriedade.id, relatorio_id=relatorio_novo.id)


# API para obter campos disponíveis
@login_required
def api_campos_disponiveis(request, propriedade_id):
    """API que retorna campos disponíveis para um módulo"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    modulo = request.GET.get('modulo', '')
    
    campos_disponiveis = _obter_campos_disponiveis()
    campos_modulo = campos_disponiveis.get(modulo, [])
    
    return JsonResponse({
        'campos': campos_modulo
    })


def _obter_campos_disponiveis():
    """Retorna campos disponíveis organizados por módulo"""
    return {
        'PECUARIA': [
            {'nome': 'numero_brinco', 'label': 'Número do Brinco', 'tipo': 'texto'},
            {'nome': 'categoria', 'label': 'Categoria', 'tipo': 'texto'},
            {'nome': 'quantidade', 'label': 'Quantidade', 'tipo': 'numero'},
            {'nome': 'valor_por_cabeca', 'label': 'Valor por Cabeça', 'tipo': 'moeda'},
            {'nome': 'valor_total', 'label': 'Valor Total', 'tipo': 'moeda'},
            {'nome': 'data_inventario', 'label': 'Data do Inventário', 'tipo': 'data'},
        ],
        'FINANCEIRO': [
            {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'texto'},
            {'nome': 'valor', 'label': 'Valor', 'tipo': 'moeda'},
            {'nome': 'data', 'label': 'Data', 'tipo': 'data'},
            {'nome': 'tipo', 'label': 'Tipo', 'tipo': 'texto'},
            {'nome': 'categoria', 'label': 'Categoria', 'tipo': 'texto'},
            {'nome': 'status', 'label': 'Status', 'tipo': 'texto'},
        ],
        'IATF': [
            {'nome': 'animal', 'label': 'Animal', 'tipo': 'texto'},
            {'nome': 'protocolo', 'label': 'Protocolo', 'tipo': 'texto'},
            {'nome': 'data_iatf', 'label': 'Data IATF', 'tipo': 'data'},
            {'nome': 'resultado', 'label': 'Resultado', 'tipo': 'texto'},
            {'nome': 'taxa_prenhez', 'label': 'Taxa de Prenhez', 'tipo': 'percentual'},
            {'nome': 'custo_total', 'label': 'Custo Total', 'tipo': 'moeda'},
        ],
        # Adicionar mais módulos conforme necessário
    }

