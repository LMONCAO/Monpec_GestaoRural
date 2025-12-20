# -*- coding: utf-8 -*-
"""
Views Consolidadas - MÓDULO OPERAÇÕES E MANUTENÇÃO
Agrupa:
- Combustível
- Manutenção de Equipamentos
- Empreiteiros
- Funcionários
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal
from datetime import date, datetime

from .models import Propriedade
from .decorators import obter_propriedade_com_permissao
from .models_operacional import (
    TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
    Empreiteiro, ServicoEmpreiteiro,
    Equipamento, ManutencaoEquipamento, TipoEquipamento
)
from .models_funcionarios import (
    Funcionario, FolhaPagamento, Holerite, PontoFuncionario, DescontoFuncionario
)
from .models_funcionarios import CalculadoraImpostos


@login_required
def operacoes_dashboard(request, propriedade_id):
    """Dashboard consolidado de Operações"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # ========== COMBUSTÍVEL ==========
    tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
    estoque_total_combustivel = sum(t.estoque_atual for t in tanques)
    
    # Consumos do mês
    mes_atual = date.today().replace(day=1)
    consumos_mes = ConsumoCombustivel.objects.filter(
        tanque__propriedade=propriedade,
        data__gte=mes_atual
    )
    total_consumo_mes = sum(c.quantidade_litros for c in consumos_mes)
    valor_consumo_mes = sum(c.valor_total for c in consumos_mes)
    
    # ========== MANUTENÇÃO ==========
    equipamentos = Equipamento.objects.filter(propriedade=propriedade, ativo=True)
    manutencoes_pendentes = ManutencaoEquipamento.objects.filter(
        equipamento__propriedade=propriedade,
        status__in=['AGENDADA', 'EM_ANDAMENTO']
    ).count()
    
    # ========== EMPREITEIROS ==========
    servicos_ativos = ServicoEmpreiteiro.objects.filter(
        propriedade=propriedade,
        status__in=['APROVADO', 'EM_ANDAMENTO']
    ).count()
    
    # ========== FUNCIONÁRIOS ==========
    funcionarios_ativos = Funcionario.objects.filter(
        propriedade=propriedade,
        situacao='ATIVO'
    ).count()
    
    folha_mensal = sum(f.salario_base for f in Funcionario.objects.filter(
        propriedade=propriedade,
        situacao='ATIVO'
    ))
    
    context = {
        'propriedade': propriedade,
        # Combustível
        'tanques': tanques,
        'estoque_total_combustivel': estoque_total_combustivel,
        'total_consumo_mes': total_consumo_mes,
        'valor_consumo_mes': valor_consumo_mes,
        # Manutenção
        'equipamentos': equipamentos,
        'manutencoes_pendentes': manutencoes_pendentes,
        # Empreiteiros
        'servicos_ativos': servicos_ativos,
        # Funcionários
        'funcionarios_ativos': funcionarios_ativos,
        'folha_mensal': folha_mensal,
    }
    
    return render(request, 'gestao_rural/operacoes_dashboard.html', context)


# ========== COMBUSTÍVEL ==========

@login_required
def combustivel_lista(request, propriedade_id):
    """Lista de tanques de combustível"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
    
    context = {
        'propriedade': propriedade,
        'tanques': tanques,
    }
    
    return render(request, 'gestao_rural/combustivel_lista.html', context)


@login_required
def consumo_combustivel_novo(request, propriedade_id):
    """Registrar consumo de combustível"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
    
    if request.method == 'POST':
        tanque_id = request.POST.get('tanque')
        tanque = get_object_or_404(TanqueCombustivel, id=tanque_id, propriedade=propriedade)
        
        consumo = ConsumoCombustivel(propriedade=propriedade, tanque=tanque)
        consumo.data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
        consumo.tipo_equipamento = request.POST.get('tipo_equipamento', '')
        consumo.identificacao = request.POST.get('identificacao', '')
        consumo.quantidade_litros = Decimal(request.POST.get('quantidade_litros', 0))
        consumo.valor_unitario = Decimal(request.POST.get('valor_unitario', 0))
        consumo.finalidade = request.POST.get('finalidade', '')
        consumo.observacoes = request.POST.get('observacoes', '')
        consumo.responsavel = request.user
        
        if consumo.quantidade_litros > tanque.estoque_atual:
            messages.error(request, f'Estoque insuficiente! Disponível: {tanque.estoque_atual}L')
            return render(request, 'gestao_rural/consumo_combustivel_form.html', {
                'propriedade': propriedade,
                'tanques': tanques
            })
        
        try:
            consumo.save()
            messages.success(request, 'Consumo registrado com sucesso!')
            return redirect('operacoes_dashboard', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar consumo: {str(e)}')
    
    return render(request, 'gestao_rural/consumo_combustivel_form.html', {
        'propriedade': propriedade,
        'tanques': tanques
    })


# ========== MANUTENÇÃO ==========

@login_required
def equipamentos_lista(request, propriedade_id):
    """Lista de equipamentos"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    equipamentos = Equipamento.objects.filter(propriedade=propriedade).select_related('tipo').order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'equipamentos': equipamentos,
    }
    
    return render(request, 'gestao_rural/equipamentos_lista.html', context)


@login_required
def manutencao_nova(request, propriedade_id):
    """Registrar nova manutenção"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    equipamentos = Equipamento.objects.filter(propriedade=propriedade, ativo=True)
    
    if request.method == 'POST':
        equipamento_id = request.POST.get('equipamento')
        equipamento = get_object_or_404(Equipamento, id=equipamento_id, propriedade=propriedade)
        
        manutencao = ManutencaoEquipamento(propriedade=propriedade, equipamento=equipamento)
        manutencao.tipo = request.POST.get('tipo')
        manutencao.descricao = request.POST.get('descricao')
        manutencao.data_agendamento = datetime.strptime(
            request.POST.get('data_agendamento'), '%Y-%m-%d'
        ).date()
        manutencao.valor_pecas = Decimal(request.POST.get('valor_pecas', 0))
        manutencao.valor_mao_obra = Decimal(request.POST.get('valor_mao_obra', 0))
        manutencao.fornecedor_servico = request.POST.get('fornecedor_servico', '')
        manutencao.status = request.POST.get('status', 'AGENDADA')
        manutencao.observacoes = request.POST.get('observacoes', '')
        manutencao.responsavel = request.user
        
        try:
            manutencao.save()
            messages.success(request, 'Manutenção registrada com sucesso!')
            return redirect('operacoes_dashboard', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar manutenção: {str(e)}')
    
    return render(request, 'gestao_rural/manutencao_form.html', {
        'propriedade': propriedade,
        'equipamentos': equipamentos
    })


# ========== FUNCIONÁRIOS ==========
# (Views já criadas em views_funcionarios.py - importar ou referenciar)


