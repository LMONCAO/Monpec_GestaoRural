# -*- coding: utf-8 -*-
"""
Views para Relatórios Oficiais SISBOV - Anexos Completos (IV a XVIII)
Conforme Instrução Normativa MAPA nº 17/2006
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q, Count, Sum
from datetime import date, datetime, timedelta
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import Propriedade, AnimalIndividual, MovimentacaoIndividual, CategoriaAnimal
try:
    from .models_reproducao import Nascimento
except ImportError:
    Nascimento = None


# ============================================================================
# ANEXO IV - CADASTRO DE PRODUTOR RURAL
# ============================================================================

@login_required
def relatorio_sisbov_anexo_iv(request, propriedade_id):
    """Anexo IV - Cadastro de Produtor Rural"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    produtor = propriedade.produtor_rural
    
    context = {
        'propriedade': propriedade,
        'produtor': produtor,
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_iv_produtor_rural.html', context)


@login_required
def relatorio_sisbov_anexo_iv_pdf(request, propriedade_id):
    """Gera PDF do Anexo IV - Cadastro de Produtor Rural"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    produtor = propriedade.produtor_rural
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_IV_Produtor_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO IV - CADASTRO DE PRODUTOR RURAL', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    if produtor:
        story.append(Paragraph(f'<b>Nome:</b> {produtor.nome}', styles['Normal']))
        story.append(Paragraph(f'<b>CPF/CNPJ:</b> {produtor.cpf_cnpj or "—"}', styles['Normal']))
        story.append(Paragraph(f'<b>RG:</b> {produtor.rg or "—"}', styles['Normal']))
        story.append(Paragraph(f'<b>Endereço:</b> {produtor.endereco or "—"}', styles['Normal']))
        story.append(Paragraph(f'<b>Telefone:</b> {produtor.telefone or "—"}', styles['Normal']))
        story.append(Paragraph(f'<b>Email:</b> {produtor.email or "—"}', styles['Normal']))
    else:
        story.append(Paragraph('Produtor rural não cadastrado.', styles['Normal']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Data:</b> {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO V - CADASTRO DE ESTABELECIMENTO RURAL
# ============================================================================

@login_required
def relatorio_sisbov_anexo_v(request, propriedade_id):
    """Anexo V - Cadastro de Estabelecimento Rural"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_v_estabelecimento_rural.html', context)


@login_required
def relatorio_sisbov_anexo_v_pdf(request, propriedade_id):
    """Gera PDF do Anexo V - Cadastro de Estabelecimento Rural"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_V_Estabelecimento_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO V - CADASTRO DE ESTABELECIMENTO RURAL', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f'<b>Nome:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Município:</b> {propriedade.municipio} - {propriedade.uf}', styles['Normal']))
    story.append(Paragraph(f'<b>Endereço:</b> {propriedade.endereco or "—"}', styles['Normal']))
    story.append(Paragraph(f'<b>CEP:</b> {propriedade.cep or "—"}', styles['Normal']))
    story.append(Paragraph(f'<b>Área Total:</b> {propriedade.area_total_ha or "—"} ha', styles['Normal']))
    story.append(Paragraph(f'<b>NIRF:</b> {propriedade.nirf or "—"}', styles['Normal']))
    story.append(Paragraph(f'<b>CAR:</b> {propriedade.car or "—"}', styles['Normal']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Data:</b> {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO IX - COMUNICADO DE ENTRADA DE ANIMAIS
# ============================================================================

@login_required
def relatorio_sisbov_anexo_ix(request, propriedade_id):
    """Anexo IX - Comunicado de Entrada de Animais"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar entradas recentes (últimos 30 dias)
    data_inicio = date.today() - timedelta(days=30)
    entradas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_destino=propriedade) | 
        (Q(animal__propriedade=propriedade) & Q(tipo_movimentacao__in=['COMPRA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO'])),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria', 'propriedade_origem').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'entradas': entradas,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_ix_entrada_animais.html', context)


@login_required
def relatorio_sisbov_anexo_ix_pdf(request, propriedade_id):
    """Gera PDF do Anexo IX - Comunicado de Entrada de Animais"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=30)
    entradas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_destino=propriedade) | 
        (Q(animal__propriedade=propriedade) & Q(tipo_movimentacao__in=['COMPRA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO'])),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'propriedade_origem').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_IX_Entrada_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO IX - COMUNICADO DE ENTRADA DE ANIMAIS', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Tipo', 'Origem', 'Peso (kg)']]
    
    for entrada in entradas:
        dados_tabela.append([
            entrada.data_movimentacao.strftime('%d/%m/%Y'),
            entrada.animal.codigo_sisbov or entrada.animal.numero_brinco or '—',
            entrada.get_tipo_movimentacao_display(),
            entrada.propriedade_origem.nome_propriedade if entrada.propriedade_origem else '—',
            str(entrada.peso_kg) if entrada.peso_kg else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 4*cm, 2*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(tabela)
    else:
        story.append(Paragraph('Nenhuma entrada registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO X - COMUNICADO DE SAÍDA DE ANIMAIS
# ============================================================================

@login_required
def relatorio_sisbov_anexo_x(request, propriedade_id):
    """Anexo X - Comunicado de Saída de Animais"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar saídas recentes (últimos 30 dias)
    data_inicio = date.today() - timedelta(days=30)
    saidas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_origem=propriedade) | 
        (Q(animal__propriedade=propriedade) & Q(tipo_movimentacao__in=['VENDA', 'TRANSFERENCIA_SAIDA', 'MORTE'])),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria', 'propriedade_destino').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'saidas': saidas,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_x_saida_animais.html', context)


@login_required
def relatorio_sisbov_anexo_x_pdf(request, propriedade_id):
    """Gera PDF do Anexo X - Comunicado de Saída de Animais"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=30)
    saidas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_origem=propriedade) | 
        (Q(animal__propriedade=propriedade) & Q(tipo_movimentacao__in=['VENDA', 'TRANSFERENCIA_SAIDA', 'MORTE'])),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'propriedade_destino').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_X_Saida_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO X - COMUNICADO DE SAÍDA DE ANIMAIS', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Tipo', 'Destino', 'Peso (kg)']]
    
    for saida in saidas:
        dados_tabela.append([
            saida.data_movimentacao.strftime('%d/%m/%Y'),
            saida.animal.codigo_sisbov or saida.animal.numero_brinco or '—',
            saida.get_tipo_movimentacao_display(),
            saida.propriedade_destino.nome_propriedade if saida.propriedade_destino else '—',
            str(saida.peso_kg) if saida.peso_kg else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 4*cm, 2*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(tabela)
    else:
        story.append(Paragraph('Nenhuma saída registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XI - DECLARAÇÃO DE NASCIMENTO
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xi(request, propriedade_id):
    """Anexo XI - Declaração de Nascimento"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar nascimentos recentes (últimos 90 dias)
    data_inicio = date.today() - timedelta(days=90)
    nascimentos = []
    
    if Nascimento:
        nascimentos = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_inicio
        ).select_related('mae', 'animal_individual').order_by('-data_nascimento')
    
    # Também buscar nascimentos via movimentações
    nascimentos_mov = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='NASCIMENTO',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'nascimentos': nascimentos,
        'nascimentos_mov': nascimentos_mov,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xi_nascimento.html', context)


@login_required
def relatorio_sisbov_anexo_xi_pdf(request, propriedade_id):
    """Gera PDF do Anexo XI - Declaração de Nascimento"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    nascimentos = []
    
    if Nascimento:
        nascimentos = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_inicio
        ).select_related('mae', 'animal_individual').order_by('-data_nascimento')
    
    nascimentos_mov = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='NASCIMENTO',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XI_Nascimento_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XI - DECLARAÇÃO DE NASCIMENTO', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Bezerro (SISBOV)', 'Mãe (SISBOV)', 'Sexo', 'Peso (kg)', 'Tipo Parto']]
    
    # Adicionar nascimentos do modelo Nascimento
    for nasc in nascimentos:
        bezerro_sisbov = nasc.animal_individual.codigo_sisbov if nasc.animal_individual else nasc.numero_brinco_bezerro or '—'
        dados_tabela.append([
            nasc.data_nascimento.strftime('%d/%m/%Y'),
            bezerro_sisbov,
            nasc.mae.codigo_sisbov or nasc.mae.numero_brinco or '—',
            nasc.get_sexo_display(),
            str(nasc.peso_nascimento) if nasc.peso_nascimento else '—',
            nasc.get_tipo_parto_display(),
        ])
    
    # Adicionar nascimentos via movimentações
    for nasc_mov in nascimentos_mov:
        dados_tabela.append([
            nasc_mov.data_movimentacao.strftime('%d/%m/%Y'),
            nasc_mov.animal.codigo_sisbov or nasc_mov.animal.numero_brinco or '—',
            nasc_mov.animal.mae.codigo_sisbov if nasc_mov.animal.mae else '—',
            nasc_mov.animal.get_sexo_display() if nasc_mov.animal.sexo else '—',
            str(nasc_mov.peso_kg) if nasc_mov.peso_kg else '—',
            '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3*cm, 3*cm, 1.5*cm, 2*cm, 2.5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(tabela)
    else:
        story.append(Paragraph('Nenhum nascimento registrado no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XII - DECLARAÇÃO DE MORTE
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xii(request, propriedade_id):
    """Anexo XII - Declaração de Morte"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar mortes recentes (últimos 90 dias)
    data_inicio = date.today() - timedelta(days=90)
    mortes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='MORTE',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    # Também buscar animais com status MORTO
    animais_mortos = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='MORTO'
    ).order_by('-data_saida', '-data_ultima_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'mortes': mortes,
        'animais_mortos': animais_mortos,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xii_morte.html', context)


@login_required
def relatorio_sisbov_anexo_xii_pdf(request, propriedade_id):
    """Gera PDF do Anexo XII - Declaração de Morte"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    mortes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='MORTE',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XII_Morte_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XII - DECLARAÇÃO DE MORTE', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Categoria', 'Motivo', 'Peso (kg)']]
    
    for morte in mortes:
        dados_tabela.append([
            morte.data_movimentacao.strftime('%d/%m/%Y'),
            morte.animal.codigo_sisbov or morte.animal.numero_brinco or '—',
            morte.animal.categoria.nome if morte.animal.categoria else '—',
            morte.observacoes or morte.motivo_detalhado or '—',
            str(morte.peso_kg) if morte.peso_kg else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 4*cm, 2*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(tabela)
    else:
        story.append(Paragraph('Nenhuma morte registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response
















