# -*- coding: utf-8 -*-
"""
Views para Gestão de Funcionários
- Processamento de folha de pagamento
- Geração de holerites
- Cálculo de impostos
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum
from decimal import Decimal
from datetime import date, datetime
from .models import Propriedade
from .decorators import obter_propriedade_com_permissao, bloquear_demo_cadastro
from .models_funcionarios import (
    Funcionario, FolhaPagamento, Holerite, PontoFuncionario,
    DescontoFuncionario, CalculadoraImpostos
)


@login_required
def funcionarios_dashboard(request, propriedade_id):
    """Dashboard de funcionários"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    funcionarios = Funcionario.objects.filter(propriedade=propriedade)
    funcionarios_ativos = funcionarios.filter(situacao='ATIVO')
    
    # Estatísticas
    total_funcionarios = funcionarios.count()
    total_ativos = funcionarios_ativos.count()
    total_folha_mensal = sum(f.salario_base for f in funcionarios_ativos)
    
    # Últimas folhas
    ultimas_folhas = FolhaPagamento.objects.filter(
        propriedade=propriedade
    ).order_by('-competencia')[:5]
    
    context = {
        'propriedade': propriedade,
        'funcionarios': funcionarios_ativos,
        'total_funcionarios': total_funcionarios,
        'total_ativos': total_ativos,
        'total_folha_mensal': total_folha_mensal,
        'ultimas_folhas': ultimas_folhas,
    }
    
    return render(request, 'gestao_rural/funcionarios_dashboard.html', context)


@login_required
def funcionarios_lista(request, propriedade_id):
    """Lista de funcionários"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    funcionarios = Funcionario.objects.filter(propriedade=propriedade).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'funcionarios': funcionarios,
    }
    
    return render(request, 'gestao_rural/funcionarios_lista.html', context)


@login_required
@bloquear_demo_cadastro
def funcionario_novo(request, propriedade_id):
    """Cadastrar novo funcionário"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        funcionario = Funcionario(propriedade=propriedade)
        funcionario.nome = request.POST.get('nome')
        funcionario.cpf = request.POST.get('cpf')
        funcionario.rg = request.POST.get('rg', '')
        if request.POST.get('data_nascimento'):
            funcionario.data_nascimento = datetime.strptime(
                request.POST.get('data_nascimento'), '%Y-%m-%d'
            ).date()
        funcionario.sexo = request.POST.get('sexo', '')
        funcionario.telefone = request.POST.get('telefone', '')
        funcionario.celular = request.POST.get('celular', '')
        funcionario.email = request.POST.get('email', '')
        funcionario.endereco = request.POST.get('endereco', '')
        funcionario.cidade = request.POST.get('cidade', '')
        funcionario.estado = request.POST.get('estado', '')
        funcionario.cep = request.POST.get('cep', '')
        funcionario.tipo_contrato = request.POST.get('tipo_contrato', 'CLT')
        funcionario.cargo = request.POST.get('cargo')
        if request.POST.get('data_admissao'):
            funcionario.data_admissao = datetime.strptime(
                request.POST.get('data_admissao'), '%Y-%m-%d'
            ).date()
        funcionario.salario_base = Decimal(request.POST.get('salario_base', 0))
        funcionario.jornada_trabalho = int(request.POST.get('jornada_trabalho', 44))
        funcionario.banco = request.POST.get('banco', '')
        funcionario.agencia = request.POST.get('agencia', '')
        funcionario.conta = request.POST.get('conta', '')
        funcionario.tipo_conta = request.POST.get('tipo_conta', '')
        funcionario.observacoes = request.POST.get('observacoes', '')
        
        try:
            funcionario.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('funcionarios_lista', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar funcionário: {str(e)}')
    
    return render(request, 'gestao_rural/funcionario_form.html', {
        'propriedade': propriedade,
        'form_type': 'novo'
    })


@login_required
def folha_pagamento_processar(request, propriedade_id):
    """Processar folha de pagamento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        competencia = request.POST.get('competencia')  # Formato: MM/AAAA
        data_vencimento = datetime.strptime(
            request.POST.get('data_vencimento'), '%Y-%m-%d'
        ).date()
        
        # Verificar se já existe folha para esta competência
        folha_existente = FolhaPagamento.objects.filter(
            propriedade=propriedade,
            competencia=competencia
        ).first()
        
        if folha_existente:
            messages.warning(request, f'Já existe uma folha de pagamento para {competencia}')
            return redirect('folha_pagamento_detalhes', propriedade_id=propriedade.id, folha_id=folha_existente.id)
        
        # Criar folha
        folha = FolhaPagamento(
            propriedade=propriedade,
            competencia=competencia,
            data_vencimento=data_vencimento
        )
        folha.save()
        
        # Processar cada funcionário ativo
        funcionarios = Funcionario.objects.filter(
            propriedade=propriedade,
            situacao='ATIVO'
        )
        
        total_proventos = Decimal('0.00')
        total_descontos = Decimal('0.00')
        
        for funcionario in funcionarios:
            holerite = processar_holerite(funcionario, folha, competencia)
            if holerite:
                total_proventos += holerite.total_proventos
                total_descontos += holerite.total_descontos
        
        # Atualizar totais da folha
        folha.total_proventos = total_proventos
        folha.total_descontos = total_descontos
        folha.total_liquido = total_proventos - total_descontos
        folha.save()
        
        messages.success(request, f'Folha de pagamento processada com sucesso!')
        return redirect('folha_pagamento_detalhes', propriedade_id=propriedade.id, folha_id=folha.id)
    
    return render(request, 'gestao_rural/folha_pagamento_processar.html', {
        'propriedade': propriedade
    })


def processar_holerite(funcionario, folha, competencia):
    """Processa holerite de um funcionário"""
    # Calcular dias trabalhados (assumindo 30 dias no mês)
    dias_trabalhados = 30
    dias_faltas = 0
    
    # Calcular salário proporcional
    salario_base = funcionario.salario_base
    if dias_faltas > 0:
        salario_base = salario_base * (Decimal(str(dias_trabalhados - dias_faltas)) / Decimal(str(dias_trabalhados)))
    
    # Calcular horas extras (se houver)
    horas_extras = Decimal('0.00')
    valor_horas_extras = Decimal('0.00')
    
    # Calcular proventos
    total_proventos = salario_base + valor_horas_extras
    
    # Calcular INSS
    base_calculo_inss = total_proventos
    desconto_inss = CalculadoraImpostos.calcular_inss(base_calculo_inss)
    
    # Calcular IRRF (base de cálculo após INSS)
    base_calculo_irrf = total_proventos - desconto_inss
    numero_dependentes = 0  # Buscar do cadastro do funcionário se necessário
    desconto_irrf = CalculadoraImpostos.calcular_irrf(base_calculo_irrf, numero_dependentes)
    
    # Calcular FGTS
    base_calculo_fgts = total_proventos
    valor_fgts = CalculadoraImpostos.calcular_fgts(base_calculo_fgts)
    
    # Buscar descontos personalizados
    descontos_ativos = DescontoFuncionario.objects.filter(
        funcionario=funcionario,
        status='ATIVO'
    )
    
    total_descontos_personalizados = Decimal('0.00')
    for desconto in descontos_ativos:
        if desconto.percentual:
            valor_desconto = total_proventos * (desconto.percentual / 100)
        else:
            valor_desconto = desconto.valor
        total_descontos_personalizados += valor_desconto
    
    # Calcular totais
    total_descontos = desconto_inss + desconto_irrf + total_descontos_personalizados
    valor_liquido = total_proventos - total_descontos
    
    # Criar holerite
    holerite = Holerite(
        folha_pagamento=folha,
        funcionario=funcionario,
        salario_base=salario_base,
        horas_extras=horas_extras,
        valor_horas_extras=valor_horas_extras,
        dias_trabalhados=dias_trabalhados,
        dias_faltas=dias_faltas,
        desconto_inss=desconto_inss,
        base_calculo_inss=base_calculo_inss,
        desconto_irrf=desconto_irrf,
        base_calculo_irrf=base_calculo_irrf,
        numero_dependentes=numero_dependentes,
        base_calculo_fgts=base_calculo_fgts,
        valor_fgts=valor_fgts,
        total_proventos=total_proventos,
        total_descontos=total_descontos,
        valor_liquido=valor_liquido
    )
    holerite.save()
    
    return holerite


@login_required
def folha_pagamento_detalhes(request, propriedade_id, folha_id):
    """Detalhes da folha de pagamento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    folha = get_object_or_404(FolhaPagamento, id=folha_id, propriedade=propriedade)
    
    holerites = Holerite.objects.filter(folha_pagamento=folha).order_by('funcionario__nome')
    
    context = {
        'propriedade': propriedade,
        'folha': folha,
        'holerites': holerites,
    }
    
    return render(request, 'gestao_rural/folha_pagamento_detalhes.html', context)


@login_required
def holerite_pdf(request, propriedade_id, holerite_id):
    """Gerar PDF do holerite"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    holerite = get_object_or_404(Holerite, id=holerite_id, folha_pagamento__propriedade=propriedade)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Cabeçalho
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"HOLERITE - {holerite.folha_pagamento.competencia}")
    
    # Dados do Funcionário
    p.setFont("Helvetica", 12)
    y = height - 100
    p.drawString(50, y, f"Funcionário: {holerite.funcionario.nome}")
    y -= 20
    p.drawString(50, y, f"CPF: {holerite.funcionario.cpf}")
    y -= 20
    p.drawString(50, y, f"Cargo: {holerite.funcionario.cargo}")
    
    # Proventos
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "PROVENTOS")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Salário Base: R$ {holerite.salario_base:.2f}")
    y -= 15
    if holerite.valor_horas_extras > 0:
        p.drawString(50, y, f"Horas Extras: R$ {holerite.valor_horas_extras:.2f}")
        y -= 15
    p.drawString(50, y, f"Total de Proventos: R$ {holerite.total_proventos:.2f}")
    
    # Descontos
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "DESCONTOS")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"INSS: R$ {holerite.desconto_inss:.2f}")
    y -= 15
    p.drawString(50, y, f"IRRF: R$ {holerite.desconto_irrf:.2f}")
    y -= 15
    p.drawString(50, y, f"Total de Descontos: R$ {holerite.total_descontos:.2f}")
    
    # Valor Líquido
    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"VALOR LÍQUIDO: R$ {holerite.valor_liquido:.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="holerite_{holerite.funcionario.cpf}_{holerite.folha_pagamento.competencia}.pdf"'
    return response


