# -*- coding: utf-8 -*-
"""
Views para exportação de dados
Exportação para Excel, PDF, etc.
"""

from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from decimal import Decimal
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether, CondPageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .relatorios_iatf import coletar_dados_iatf, IATFModuloIndisponivel


def calcular_altura_tabela(table_data, font_size=10, padding=8):
    """
    Calcula a altura aproximada de uma tabela baseada no número de linhas e fonte
    """
    num_linhas = len(table_data)
    altura_linha = font_size + padding + 4  # Adicionar margem extra
    altura_total = num_linhas * altura_linha
    return altura_total


def ajustar_tabela_para_pagina(table_data, col_widths, max_height_cm=20):
    """
    Ajusta uma tabela para caber na página, dividindo se necessário
    Inclui cabeçalho em cada parte dividida
    """
    if len(table_data) <= 1:
        return [table_data]
    
    # Altura máxima disponível (reduzida para evitar problemas)
    altura_maxima_pt = max_height_cm * 28.35  # Converter cm para pontos
    
    # Calcular altura aproximada por linha (incluindo cabeçalho)
    altura_linha = 25  # Altura aproximada por linha em pontos
    altura_cabecalho = 40  # Altura do cabeçalho
    
    # Calcular quantas linhas cabem (excluindo cabeçalho)
    linhas_disponiveis = int((altura_maxima_pt - altura_cabecalho) / altura_linha)
    linhas_disponiveis = max(5, linhas_disponiveis)  # Mínimo de 5 linhas por página
    
    # Se a tabela cabe em uma página, retornar sem dividir
    if len(table_data) <= linhas_disponiveis + 1:  # +1 para cabeçalho
        return [table_data]
    
    # Dividir a tabela mantendo cabeçalho em cada parte
    tabelas_divididas = []
    cabecalho = table_data[0]  # Primeira linha é o cabeçalho
    dados = table_data[1:]  # Resto são os dados
    
    for i in range(0, len(dados), linhas_disponiveis):
        parte_dados = dados[i:i + linhas_disponiveis]
        # Incluir cabeçalho em cada parte
        parte_tabela = [cabecalho] + parte_dados
        tabelas_divididas.append(parte_tabela)
    
    return tabelas_divididas


def ajustar_fonte_por_conteudo(table_data, fonte_base=10):
    """
    Ajusta o tamanho da fonte baseado na quantidade de conteúdo
    """
    num_linhas = len(table_data)
    
    if num_linhas <= 10:
        return fonte_base  # Fonte normal
    elif num_linhas <= 20:
        return fonte_base - 1  # Fonte um pouco menor
    elif num_linhas <= 30:
        return fonte_base - 2  # Fonte menor
    else:
        return fonte_base - 3  # Fonte bem menor


def calcular_larguras_dinamicas(table_data, num_colunas, largura_total_cm=27.7):
    """
    Calcula larguras de colunas dinamicamente baseado no conteúdo e número de colunas
    """
    # Percentuais de largura por número de colunas
    if num_colunas == 6:
        # Tabela de inventário: 6 colunas
        percentuais = [25, 10, 12, 12, 12, 21]  # Categoria 25%, valores 10-12%, Total 21%
    elif num_colunas == 11:
        # Verificar se é tabela de projeção por ano (tem "Saldo Inicial" no cabeçalho)
        if table_data and len(table_data) > 0 and 'Saldo' in str(table_data[0]):
            # Tabela de projeção por ano: 11 colunas (ajustado para cabeçalhos)
            # Distribuir melhor para evitar quebra de linha nos cabeçalhos
            percentuais = [16, 7, 8, 7, 7, 7, 9, 7, 7, 9, 15]  # Categoria 16%, Valores 7-9%, Total 15%
        else:
            # Tabela de evolução: 11 colunas
            percentuais = [15, 8, 8, 8, 8, 10, 8, 8, 8, 8, 15]  # Categoria 15%, Total 15%
    else:
        # Distribuição padrão para outras tabelas
        percentuais = [100 / num_colunas] * num_colunas
        if num_colunas >= 6:
            # Primeira coluna maior
            percentuais[0] = (100 / num_colunas) * 1.8
            # Redistribuir o resto
            ajuste = (percentuais[0] - (100 / num_colunas)) / (num_colunas - 1)
            for i in range(1, num_colunas):
                percentuais[i] -= ajuste
    
    # Converter para cm e depois para unidades do ReportLab
    larguras = [(largura_total_cm * p / 100) for p in percentuais]
    
    return [largura * cm for largura in larguras]


@login_required
def exportar_inventario_excel(request, propriedade_id):
    """Exporta inventário para Excel com cabeçalho formatado"""
    from .models import InventarioRebanho, Propriedade
    from datetime import datetime
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar inventário mais recente
    inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').order_by('-data_inventario').first()
    
    if not inventario_recente:
        from django.contrib import messages
        messages.warning(request, 'Nenhum inventário encontrado para exportar.')
        from django.shortcuts import redirect
        return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    data_inventario = inventario_recente.data_inventario
    
    # Buscar todos os itens do inventário na mesma data
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario=data_inventario
    ).select_related('categoria').order_by('categoria__sexo', 'categoria__idade_minima_meses')
    
    # Criar workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventário do Rebanho"
    
    # Estilos
    title_font = Font(name='Arial', size=18, bold=True, color='FFFFFF')
    subtitle_font = Font(name='Arial', size=11, color='FFFFFF')
    header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    normal_font = Font(name='Arial', size=10)
    bold_font = Font(name='Arial', size=10, bold=True)
    total_font = Font(name='Arial', size=11, bold=True)
    
    # Cores
    azul_escuro = PatternFill(start_color="1e3a5f", end_color="1e3a5f", fill_type="solid")
    azul_medio = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    cinza_claro = PatternFill(start_color="f2f2f2", end_color="f2f2f2", fill_type="solid")
    verde_claro = PatternFill(start_color="d4edda", end_color="d4edda", fill_type="solid")
    
    # ===== CABEÇALHO =====
    # Título principal
    ws['A1'] = 'RELATÓRIO DE INVENTÁRIO DO REBANHO'
    ws['A1'].font = title_font
    ws['A1'].fill = azul_escuro
    ws.merge_cells('A1:F1')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    
    # Informações da propriedade
    ws['A2'] = f'Propriedade: {propriedade.nome_propriedade}'
    ws['A2'].font = subtitle_font
    ws['A2'].fill = azul_medio
    ws.merge_cells('A2:F2')
    ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 25
    
    # Localização e data
    localizacao = f'{propriedade.municipio}/{propriedade.uf}' if propriedade.municipio else ''
    ws['A3'] = f'{localizacao} | Data do Inventário: {data_inventario.strftime("%d/%m/%Y")} | Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    ws['A3'].font = Font(name='Arial', size=9, color='FFFFFF')
    ws['A3'].fill = azul_medio
    ws.merge_cells('A3:F3')
    ws['A3'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[3].height = 20
    
    # Espaço
    ws.row_dimensions[4].height = 10
    
    # ===== CABEÇALHO DA TABELA =====
    headers = ['Categoria', 'Idade', 'Sexo', 'Quantidade', 'Valor por Cabeça (R$)', 'Valor Total (R$)']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=header)
        cell.font = header_font
        cell.fill = azul_medio
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = Border(
            left=Side(style='thin', color='FFFFFF'),
            right=Side(style='thin', color='FFFFFF'),
            top=Side(style='thin', color='FFFFFF'),
            bottom=Side(style='thin', color='FFFFFF')
        )
    ws.row_dimensions[5].height = 30
    
    # ===== DADOS DO INVENTÁRIO =====
    row = 6
    total_quantidade = 0
    total_valor = Decimal('0.00')
    
    # Separar por sexo
    femeas = []
    machos = []
    
    for item in inventario:
        if item.categoria.sexo == 'F':
            femeas.append(item)
        elif item.categoria.sexo == 'M':
            machos.append(item)
        else:
            femeas.append(item)  # Default
    
    # Fêmeas primeiro
    for item in femeas:
        idade_str = ''
        if item.categoria.idade_minima_meses is not None and item.categoria.idade_maxima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}-{item.categoria.idade_maxima_meses} M'
        elif item.categoria.idade_minima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}+ M'
        elif item.categoria.idade_maxima_meses is not None:
            idade_str = f'Até {item.categoria.idade_maxima_meses} M'
        
        sexo_str = item.categoria.get_sexo_display() if hasattr(item.categoria, 'get_sexo_display') else ('Fêmea' if item.categoria.sexo == 'F' else 'Macho')
        
        ws.cell(row=row, column=1, value=item.categoria.nome).font = normal_font
        ws.cell(row=row, column=2, value=idade_str).font = normal_font
        ws.cell(row=row, column=3, value=sexo_str).font = normal_font
        ws.cell(row=row, column=4, value=item.quantidade).font = normal_font
        ws.cell(row=row, column=5, value=float(item.valor_por_cabeca)).number_format = '#,##0.00'
        ws.cell(row=row, column=5).font = normal_font
        
        valor_total = float(item.valor_total) if item.valor_total else 0.0
        ws.cell(row=row, column=6, value=valor_total).number_format = '#,##0.00'
        ws.cell(row=row, column=6).font = normal_font
        
        # Alternar cor de fundo
        if row % 2 == 0:
            for col in range(1, 7):
                ws.cell(row=row, column=col).fill = cinza_claro
        
        # Bordas
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            ws.cell(row=row, column=col).alignment = Alignment(
                horizontal='center' if col > 1 else 'left',
                vertical='center'
            )
        
        total_quantidade += item.quantidade
        total_valor += Decimal(str(valor_total))
        row += 1
    
    # Machos
    for item in machos:
        idade_str = ''
        if item.categoria.idade_minima_meses is not None and item.categoria.idade_maxima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}-{item.categoria.idade_maxima_meses} M'
        elif item.categoria.idade_minima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}+ M'
        elif item.categoria.idade_maxima_meses is not None:
            idade_str = f'Até {item.categoria.idade_maxima_meses} M'
        
        sexo_str = item.categoria.get_sexo_display() if hasattr(item.categoria, 'get_sexo_display') else ('Fêmea' if item.categoria.sexo == 'F' else 'Macho')
        
        ws.cell(row=row, column=1, value=item.categoria.nome).font = normal_font
        ws.cell(row=row, column=2, value=idade_str).font = normal_font
        ws.cell(row=row, column=3, value=sexo_str).font = normal_font
        ws.cell(row=row, column=4, value=item.quantidade).font = normal_font
        ws.cell(row=row, column=5, value=float(item.valor_por_cabeca)).number_format = '#,##0.00'
        ws.cell(row=row, column=5).font = normal_font
        
        valor_total = float(item.valor_total) if item.valor_total else 0.0
        ws.cell(row=row, column=6, value=valor_total).number_format = '#,##0.00'
        ws.cell(row=row, column=6).font = normal_font
        
        # Alternar cor de fundo
        if row % 2 == 0:
            for col in range(1, 7):
                ws.cell(row=row, column=col).fill = cinza_claro
        
        # Bordas
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            ws.cell(row=row, column=col).alignment = Alignment(
                horizontal='center' if col > 1 else 'left',
                vertical='center'
            )
        
        total_quantidade += item.quantidade
        total_valor += Decimal(str(valor_total))
        row += 1
    
    # ===== LINHA DE TOTAIS =====
    ws.row_dimensions[row].height = 25
    ws.cell(row=row, column=1, value='TOTAIS').font = total_font
    ws.cell(row=row, column=1).fill = verde_claro
    ws.cell(row=row, column=2, value='-').font = total_font
    ws.cell(row=row, column=2).fill = verde_claro
    ws.cell(row=row, column=3, value='-').font = total_font
    ws.cell(row=row, column=3).fill = verde_claro
    ws.cell(row=row, column=4, value=total_quantidade).font = total_font
    ws.cell(row=row, column=4).fill = verde_claro
    ws.cell(row=row, column=5, value='-').font = total_font
    ws.cell(row=row, column=5).fill = verde_claro
    ws.cell(row=row, column=6, value=float(total_valor)).number_format = '#,##0.00'
    ws.cell(row=row, column=6).font = total_font
    ws.cell(row=row, column=6).fill = verde_claro
    
    # Bordas na linha de totais
    for col in range(1, 7):
        ws.cell(row=row, column=col).border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )
        ws.cell(row=row, column=col).alignment = Alignment(
            horizontal='center' if col > 1 else 'left',
            vertical='center'
        )
    
    # ===== AJUSTAR LARGURAS DAS COLUNAS =====
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 22
    ws.column_dimensions['F'].width = 22
    
    # ===== PREPARAR RESPOSTA =====
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    nome_arquivo = f'inventario_{propriedade.nome_propriedade.replace(" ", "_")}_{data_inventario.strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    wb.save(response)
    return response


@login_required
def exportar_projecao_excel(request, propriedade_id):
    """Exporta projeção para Excel"""
    from .models import MovimentacaoProjetada, Propriedade
    from decimal import Decimal
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').order_by('data_movimentacao')
    
    # Criar workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Projeção"
    
    # Estilizar cabeçalho
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    ws['A1'] = 'Data'
    ws['B1'] = 'Tipo Movimentação'
    ws['C1'] = 'Categoria'
    ws['D1'] = 'Quantidade'
    ws['E1'] = 'Valor Unitário'
    ws['F1'] = 'Valor Total'
    ws['G1'] = 'Observação'
    
    # Aplicar estilo ao cabeçalho
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Preencher dados
    row = 2
    for mov in movimentacoes:
        ws[f'A{row}'] = mov.data_movimentacao.strftime('%d/%m/%Y')
        ws[f'B{row}'] = mov.get_tipo_movimentacao_display()
        ws[f'C{row}'] = mov.categoria.nome
        ws[f'D{row}'] = mov.quantidade
        ws[f'E{row}'] = float(mov.valor_por_cabeca) if mov.valor_por_cabeca else 0
        ws[f'F{row}'] = float(mov.valor_total) if mov.valor_total else 0
        ws[f'G{row}'] = mov.observacao or ''
        row += 1
    
    # Ajustar largura das colunas
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 40
    
    # Preparar resposta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="projecao_{propriedade.id}.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_projecao_pdf(request, propriedade_id):
    """Exporta projeção para PDF em modo paisagem com todas as tabelas"""
    from .models import MovimentacaoProjetada, Propriedade, InventarioRebanho, ParametrosProjecaoRebanho, CategoriaAnimal
    from .views import gerar_resumo_projecao_por_ano, gerar_evolucao_detalhada_rebanho
    from datetime import datetime
    from collections import defaultdict
    from decimal import Decimal
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar dados
    movimentacoes = list(MovimentacaoProjetada.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').order_by('data_movimentacao'))
    
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade).select_related('categoria')
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    if not movimentacoes:
        from django.contrib import messages
        messages.error(request, 'Nenhuma projeção encontrada. Gere uma projeção primeiro.')
        from django.shortcuts import redirect
        return redirect('pecuaria_projecao', propriedade_id=propriedade.id)
    
    # Gerar resumo por ano
    resumo_projecao_por_ano = gerar_resumo_projecao_por_ano(movimentacoes, inventario, propriedade)
    evolucao_detalhada = gerar_evolucao_detalhada_rebanho(movimentacoes, inventario)
    
    # Calcular evolução do rebanho para o gráfico
    evolucao_rebanho = []
    if resumo_projecao_por_ano:
        for ano in sorted(resumo_projecao_por_ano.keys()):
            dados = resumo_projecao_por_ano[ano]
            evolucao_rebanho.append({
                'ano': ano,
                'saldo_inicial': dados.get('totais', {}).get('saldo_inicial_total', 0),
                'saldo_final': dados.get('totais', {}).get('saldo_final_total', 0),
            })
    
    # Gerar gráfico de evolução do rebanho
    grafico_bytes = None
    if evolucao_rebanho and len(evolucao_rebanho) > 0:
        try:
            import matplotlib
            matplotlib.use('Agg')  # Backend não-interativo
            import matplotlib.pyplot as plt
            from io import BytesIO
            import numpy as np
            
            # Preparar dados
            anos = [item['ano'] for item in evolucao_rebanho]
            saldos_inicial = [float(item['saldo_inicial']) for item in evolucao_rebanho]
            saldos_final = [float(item['saldo_final']) for item in evolucao_rebanho]
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plotar linhas
            ax.plot(anos, saldos_inicial, marker='o', linewidth=2.5, markersize=8, 
                   label='Saldo Inicial', color='#36a2eb', linestyle='-')
            ax.plot(anos, saldos_final, marker='s', linewidth=2.5, markersize=8, 
                   label='Saldo Final', color='#4bc0c0', linestyle='-')
            
            # Preencher área entre as linhas
            ax.fill_between(anos, saldos_inicial, alpha=0.2, color='#36a2eb')
            ax.fill_between(anos, saldos_final, alpha=0.2, color='#4bc0c0')
            
            # Configurar gráfico
            ax.set_xlabel('Ano', fontsize=12, fontweight='bold')
            ax.set_ylabel('Quantidade de Animais', fontsize=12, fontweight='bold')
            ax.set_title('Evolução do Rebanho por Ano', fontsize=14, fontweight='bold', pad=15)
            ax.legend(loc='best', fontsize=11, framealpha=0.9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xticks(anos)
            
            # Formatar eixos
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar em BytesIO
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            grafico_bytes = buffer
            plt.close(fig)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao gerar gráfico de evolução: {e}")
            grafico_bytes = None
    
    # Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    data_atual = datetime.now().strftime('%Y%m%d')
    response['Content-Disposition'] = f'attachment; filename="projecao_{propriedade.id}_{data_atual}.pdf"'
    
    # Criar documento PDF em paisagem
    from reportlab.lib.pagesizes import landscape, A4
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    
    # Estilos profissionais
    styles = getSampleStyleSheet()
    
    # Título principal mais elegante
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=8,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=26
    )
    
    # Seções principais mais destacadas
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leading=20,
        borderWidth=0,
        borderColor=colors.HexColor('#1e3a8a'),
        borderPadding=2
    )
    
    # Subseções mais elegantes
    subsection_style = ParagraphStyle(
        'SubSectionStyle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#6495ed'),
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        leading=18
    )
    
    # Estilo para texto normal mais legível
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        spaceBefore=2,
        fontName='Helvetica',
        leading=14
    )
    
    # Cabeçalho profissional
    story.append(Spacer(1, 0.5*cm))
    
    # Logo/Identificação da empresa
    logo_text = Paragraph("MONPEC", ParagraphStyle(
        'LogoStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=0,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    story.append(logo_text)
    
    subtitle_text = Paragraph("MONITOR DA PECUARIA", ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    story.append(subtitle_text)
    
    # Linha divisória
    story.append(Spacer(1, 0.2*cm))
    line = Table([['']], colWidths=[27.7*cm])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (0, 0), 2, colors.HexColor('#1e3a8a'))]))
    story.append(line)
    story.append(Spacer(1, 0.3*cm))
    
    # Título principal
    story.append(Paragraph("Relatório de Gado", title_style))
    story.append(Spacer(1, 0.4*cm))
    
    # Informações detalhadas da propriedade
    info_table_data = [
        ['Propriedade:', propriedade.nome_propriedade, 'Período:', f"{min(resumo_projecao_por_ano.keys()) if resumo_projecao_por_ano else 'N/A'} - {max(resumo_projecao_por_ano.keys()) if resumo_projecao_por_ano else 'N/A'}"],
        ['Produtor:', propriedade.produtor.nome if propriedade.produtor else 'N/A', 'Data:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ['Localização:', f"{getattr(propriedade, 'cidade', 'N/A')}, {getattr(propriedade, 'estado', 'N/A')}" if getattr(propriedade, 'cidade', None) and getattr(propriedade, 'estado', None) else 'N/A', 'Anos Projetados:', str(len(resumo_projecao_por_ano)) if resumo_projecao_por_ano else '0']
    ]
    
    info_table = Table(info_table_data, colWidths=[3.5*cm, 8.5*cm, 3.5*cm, 8.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),  # Borda externa grossa
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.8*cm))
    
    # Resumo Executivo
    story.append(Paragraph("RESUMO EXECUTIVO", section_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Calcular indicadores principais
    total_animais_inicial = sum(item.quantidade for item in inventario) if inventario.exists() else 0
    valor_total_rebanho = sum(float(item.valor_total or 0) for item in inventario) if inventario.exists() else 0
    
    # Calcular principais movimentações
    total_nascimentos = sum(dados.get('nascimentos', 0) for dados in evolucao_detalhada.values()) if evolucao_detalhada else 0
    total_vendas = sum(dados.get('vendas', 0) for dados in evolucao_detalhada.values()) if evolucao_detalhada else 0
    total_compras = sum(dados.get('compras', 0) for dados in evolucao_detalhada.values()) if evolucao_detalhada else 0
    
    # Card de indicadores principais
    indicadores_data = [
        ['INDICADORES PRINCIPAIS', '', '', ''],
        ['Total de Animais Inicial:', f"{total_animais_inicial:,}".replace(',', '.'), 'Valor Total do Rebanho:', f"R$ {valor_total_rebanho:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')],
        ['Total de Nascimentos:', f"{total_nascimentos:,}".replace(',', '.'), 'Total de Vendas:', f"{total_vendas:,}".replace(',', '.')],
        ['Total de Compras:', f"{total_compras:,}".replace(',', '.'), 'Anos Projetados:', str(len(resumo_projecao_por_ano)) if resumo_projecao_por_ano else '0'],
    ]
    
    indicadores_table = Table(indicadores_data, colWidths=[6.5*cm, 4.5*cm, 6.5*cm, 4.5*cm])
    indicadores_table.setStyle(TableStyle([
        # Cabeçalho da tabela
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Dados da tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#1e3a8a')),
        
        # Bordas e espaçamento
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),  # Borda externa grossa
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        
        # Alternância de cores nas linhas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(indicadores_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Adicionar seção de Parâmetros e Resumo de Nascimentos
    if parametros:
        story.append(Paragraph("PARÂMETROS DE PROJEÇÃO", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        parametros_data = [
            ['Parâmetro', 'Valor'],
            ['Taxa de Natalidade Anual:', f"{parametros.taxa_natalidade_anual}%"],
            ['Taxa de Mortalidade Bezerros:', f"{parametros.taxa_mortalidade_bezerros_anual}%"],
            ['Taxa de Mortalidade Adultos:', f"{parametros.taxa_mortalidade_adultos_anual}%"],
        ]
        
        if hasattr(parametros, 'taxa_inflacao_anual') and parametros.taxa_inflacao_anual:
            parametros_data.append(['Taxa de Inflação Anual:', f"{parametros.taxa_inflacao_anual}%"])
        
        parametros_table = Table(parametros_data, colWidths=[12*cm, 12*cm])
        parametros_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(parametros_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Resumo de Nascimentos por Ano
    if resumo_projecao_por_ano:
        story.append(Paragraph("RESUMO DE NASCIMENTOS", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        nascimentos_data = [['Ano', 'Total de Nascimentos', 'Bezerros (M)', 'Bezerras (F)']]
        total_nascimentos_geral = 0
        total_bezerros = 0
        total_bezerras = 0
        
        for ano, dados_ano in sorted(resumo_projecao_por_ano.items()):
            totais = dados_ano.get('totais', {})
            nascimentos_ano = totais.get('nascimentos_total', 0)
            
            # Calcular bezerros e bezerras do ano
            bezerros_ano = 0
            bezerras_ano = 0
            for mov in movimentacoes:
                if mov.data_movimentacao.year == ano and mov.tipo_movimentacao == 'NASCIMENTO':
                    categoria_nome = mov.categoria.nome
                    # Verificar se é bezerro macho (o) ou bezerra fêmea (a)
                    if 'Bezerro(o)' in categoria_nome or ('Bezerro' in categoria_nome and 'Bezerra' not in categoria_nome and 'Bezerro(a)' not in categoria_nome):
                        bezerros_ano += mov.quantidade
                    elif 'Bezerro(a)' in categoria_nome or 'Bezerra' in categoria_nome:
                        bezerras_ano += mov.quantidade
            
            total_nascimentos_geral += nascimentos_ano
            total_bezerros += bezerros_ano
            total_bezerras += bezerras_ano
            
            nascimentos_data.append([
                str(ano),
                f"{nascimentos_ano:,}".replace(',', '.'),
                f"{bezerros_ano:,}".replace(',', '.'),
                f"{bezerras_ano:,}".replace(',', '.')
            ])
        
        # Adicionar linha de totais (usar strings simples, não HTML)
        nascimentos_data.append([
            'TOTAL',
            f"{total_nascimentos_geral:,}".replace(',', '.'),
            f"{total_bezerros:,}".replace(',', '.'),
            f"{total_bezerras:,}".replace(',', '.')
        ])
        
        nascimentos_table = Table(nascimentos_data, colWidths=[4*cm, 6*cm, 6*cm, 6*cm])
        nascimentos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(nascimentos_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Resumo de Reprodução (Primíparas e Matrizes)
    if resumo_projecao_por_ano:
        story.append(Paragraph("RESUMO DE REPRODUÇÃO", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        reproducao_data = [['Ano', 'Matrizes em Reprodução', 'Primíparas', '80% Primíparas em Reprodução', '20% Primíparas Vendidas']]
        
        for ano, dados_ano in sorted(resumo_projecao_por_ano.items()):
            categorias = dados_ano.get('categorias', {})
            
            # Buscar matrizes e primíparas
            matrizes = categorias.get('Vacas em Reprodução +36 M', {})
            primiparas = categorias.get('Primíparas 24-36 M', {})
            
            saldo_matrizes = matrizes.get('saldo_final', 0) if matrizes else 0
            saldo_primiparas = primiparas.get('saldo_final', 0) if primiparas else 0
            primiparas_reproducao = int(saldo_primiparas * 0.80) if saldo_primiparas else 0
            primiparas_vendidas = int(saldo_primiparas * 0.20) if saldo_primiparas else 0
            
            reproducao_data.append([
                str(ano),
                f"{saldo_matrizes:,}".replace(',', '.'),
                f"{saldo_primiparas:,}".replace(',', '.'),
                f"{primiparas_reproducao:,}".replace(',', '.'),
                f"{primiparas_vendidas:,}".replace(',', '.')
            ])
        
        reproducao_table = Table(reproducao_data, colWidths=[4*cm, 5*cm, 5*cm, 5*cm, 5*cm])
        reproducao_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(reproducao_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Resumo de Transferências (usar KeepTogether para manter título, tabela e total juntos)
    if resumo_projecao_por_ano:
        transferencias_section = []
        transferencias_section.append(Paragraph("RESUMO DE TRANSFERÊNCIAS", section_style))
        transferencias_section.append(Spacer(1, 0.3*cm))
        
        transferencias_data = [['Ano', 'Transferências Entrada', 'Transferências Saída', 'Saldo Líquido']]
        total_entrada = 0
        total_saida = 0
        
        for ano, dados_ano in sorted(resumo_projecao_por_ano.items()):
            totais = dados_ano.get('totais', {})
            entrada = totais.get('transferencias_entrada_total', 0)
            saida = totais.get('transferencias_saida_total', 0)
            saldo = entrada - saida
            
            total_entrada += entrada
            total_saida += saida
            
            transferencias_data.append([
                str(ano),
                f"{entrada:,}".replace(',', '.'),
                f"{saida:,}".replace(',', '.'),
                f"{saldo:,}".replace(',', '.')
            ])
        
        # Adicionar linha de totais (usar strings simples, não HTML)
        transferencias_data.append([
            'TOTAL',
            f"{total_entrada:,}".replace(',', '.'),
            f"{total_saida:,}".replace(',', '.'),
            f"{total_entrada - total_saida:,}".replace(',', '.')
        ])
        
        transferencias_table = Table(transferencias_data, colWidths=[4*cm, 6*cm, 6*cm, 6*cm])
        transferencias_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        transferencias_section.append(transferencias_table)
        transferencias_section.append(Spacer(1, 0.3*cm))
        
        # Manter toda a seção junta
        story.append(KeepTogether(transferencias_section))
    
    # Índice/Sumário - em página dedicada
    # Quebra de página antes do índice para garantir página própria
    story.append(PageBreak())
    
    # Criar seção do índice para manter junto
    indice_section = []
    indice_section.append(Paragraph("ÍNDICE", section_style))
    indice_section.append(Spacer(1, 0.3*cm))
    
    indice_data = [['Seção', 'Página']]
    pagina_atual = 2  # Começando da página 2 (após resumo executivo)
    
    # Removido: Inventário Inicial e Evolução Detalhada conforme solicitado
    
    if resumo_projecao_por_ano:
        indice_data.append(['1. Projeção por Ano', str(pagina_atual)])
        for ano in sorted(resumo_projecao_por_ano.keys()):
            indice_data.append([f'   1.{ano}. Projeção {ano}', str(pagina_atual)])
            pagina_atual += 1
    
    # Adicionar análise financeira ao índice
    indice_data.append(['2. Análise Financeira', str(pagina_atual)])
    
    indice_table = Table(indice_data, colWidths=[21*cm, 3*cm])
    indice_table.setStyle(TableStyle([
        # Cabeçalho da tabela
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Dados da tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Bordas e espaçamento
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),  # Borda externa grossa
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        # Alternância de cores nas linhas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    # Adicionar tabela à seção
    indice_section.append(indice_table)
    
    # Manter toda a seção do índice junta e em página própria
    story.append(KeepTogether(indice_section))
    
    # Quebra de página após o índice para separar das próximas seções
    story.append(PageBreak())
    
    # Seções removidas conforme solicitado:
    # - 1. INVENTÁRIO INICIAL
    # - 2. EVOLUÇÃO DETALHADA DO REBANHO
    
    # Adicionar tabelas por ano (formato paginado igual à tela)
    if resumo_projecao_por_ano:
        anos_ordenados = sorted(resumo_projecao_por_ano.keys())
        for idx, ano in enumerate(anos_ordenados):
            dados_ano = resumo_projecao_por_ano[ano]
            # Adicionar quebra de página apenas se não for o primeiro ano
            # Se for o primeiro ano e há evolução detalhada, adicionar espaçador ao invés de quebra
            # Usar CondPageBreak para evitar páginas em branco
            if idx > 0:
                story.append(CondPageBreak(5*cm))  # Quebra apenas se necessário
            elif not evolucao_detalhada and idx == 0:
                # Se não há evolução detalhada, adicionar quebra condicional antes do primeiro ano
                story.append(CondPageBreak(5*cm))
            else:
                # Se há evolução detalhada e é o primeiro ano, adicionar espaçador maior
                story.append(Spacer(1, 0.8*cm))
            story.append(Spacer(1, 0.3*cm))
            
            # Cabeçalho do ano (igual à tela)
            header_style = ParagraphStyle(
                'YearHeader',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1e3a8a'),
                spaceAfter=6,
                spaceBefore=0,
                fontName='Helvetica-Bold',
                leading=20
            )
            
            # Criar seção do ano (cabeçalho + tabela) para manter junto
            ano_section = []
            
            # Montar cabeçalho com informações do proprietário e propriedade
            header_text = f"Projeção do Ano {ano}"
            if propriedade.produtor:
                header_text = f"{propriedade.produtor.nome} - {propriedade.nome_propriedade} - {header_text}"
                if propriedade.inscricao_estadual:
                    header_text += f" (IE: {propriedade.inscricao_estadual})"
                elif propriedade.produtor.cpf_cnpj:
                    header_text += f" (CPF/CNPJ: {propriedade.produtor.cpf_cnpj})"
            else:
                header_text = f"{propriedade.nome_propriedade} - {header_text}"
            
            ano_section.append(Paragraph(header_text, header_style))
            ano_section.append(Spacer(1, 0.2*cm))
            
            # Informação sobre saldo inicial
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                spaceAfter=8,
                spaceBefore=0
            )
            
            if dados_ano.get('ano_anterior'):
                saldo_anterior = dados_ano.get('saldo_final_ano_anterior', 0)
                info_text = f"<b>Saldo Inicial:</b> Baseado no saldo final do ano {dados_ano.get('ano_anterior')} ({int(saldo_anterior):,} cabeças)".replace(',', '.')
            else:
                saldo_inicial = dados_ano.get('totais', {}).get('saldo_inicial_total', 0)
                info_text = f"<b>Saldo Inicial:</b> Baseado no inventário cadastrado ({int(saldo_inicial):,} cabeças)".replace(',', '.')
            
            ano_section.append(Paragraph(info_text, info_style))
            ano_section.append(Spacer(1, 0.3*cm))
            
            # Tabela de dados com cabeçalhos - "Saldo Inicial" quebra em duas linhas
            table_data = [[
                'Categoria', 
                'Saldo<br/>Inicial', 
                'Nascimentos', 
                'Compras', 
                'Vendas', 
                'Mortes', 
                'Transferências', 
                'Evolução', 
                'Saldo Final', 
                'Valor Unit. (R$)', 
                'Valor Total (R$)'
            ]]
            
            # Usar estrutura correta: dados_ano['categorias']
            categorias_ano = dados_ano.get('categorias', {})
            
            # Filtrar categorias que não têm dados relevantes (saldo inicial = 0, saldo final = 0, sem movimentações)
            # e ordenar: fêmeas primeiro, depois machos, depois por idade
            categorias_filtradas = []
            for categoria, dados in categorias_ano.items():
                saldo_inicial = dados.get('saldo_inicial', 0) or 0
                saldo_final = dados.get('saldo_final', 0) or 0
                nascimentos = dados.get('nascimentos', 0) or 0
                compras = dados.get('compras', 0) or 0
                vendas = dados.get('vendas', 0) or 0
                mortes = dados.get('mortes', 0) or 0
                trans_entrada = dados.get('transferencias_entrada', 0) or 0
                trans_saida = dados.get('transferencias_saida', 0) or 0
                evolucao = dados.get('evolucao_categoria', 0) or 0
                
                # Incluir categoria se tiver qualquer dado relevante
                # IMPORTANTE: Excluir "Bezerro(a) 0-12 M" que não deveria existir (é duplicado de "Bezerro(o) 0-12 M")
                tem_dados = (saldo_inicial > 0 or saldo_final > 0 or nascimentos > 0 or 
                            compras > 0 or vendas > 0 or mortes > 0 or 
                            trans_entrada > 0 or trans_saida > 0 or evolucao != 0)
                
                # Excluir categoria "Bezerro(a) 0-12 M" que não deveria existir
                if categoria == 'Bezerro(a) 0-12 M':
                    continue  # Pular esta categoria
                
                if tem_dados:
                    # Buscar categoria no banco para obter sexo e idade
                    try:
                        categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                        # Determinar ordem de sexo: Fêmeas primeiro (1), Machos segundo (2), Indefinidos terceiro (3)
                        if categoria_obj.sexo == 'F':
                            ordem_sexo = 1  # Fêmeas primeiro
                        elif categoria_obj.sexo == 'M':
                            ordem_sexo = 2  # Machos segundo
                        else:
                            ordem_sexo = 3  # Indefinidos
                        
                        # Idade mínima para ordenação (usar 999 se None para colocar no final)
                        idade_minima = categoria_obj.idade_minima_meses if categoria_obj.idade_minima_meses is not None else 999
                        idade_maxima = categoria_obj.idade_maxima_meses if categoria_obj.idade_maxima_meses is not None else 999
                    except CategoriaAnimal.DoesNotExist:
                        # Fallback: tentar determinar pelo nome
                        if 'fêmea' in categoria.lower() or 'femea' in categoria.lower() or categoria.endswith(' F'):
                            ordem_sexo = 1  # Fêmeas primeiro
                        elif 'macho' in categoria.lower() or categoria.endswith(' M') or 'bezerro(o)' in categoria.lower() or 'garrote' in categoria.lower() or 'boi' in categoria.lower() or 'touro' in categoria.lower():
                            ordem_sexo = 2  # Machos segundo
                        else:
                            ordem_sexo = 3  # Indefinidos
                        idade_minima = 999
                        idade_maxima = 999
                    
                    categorias_filtradas.append((ordem_sexo, idade_minima, idade_maxima, categoria, dados))
            
            # Ordenar: primeiro por sexo, depois por idade mínima, depois por idade máxima, depois por nome
            categorias_filtradas.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
            
            for ordem_sexo, idade_minima, idade_maxima, categoria, dados in categorias_filtradas:
                # Formatar transferências
                trans_entrada = dados.get('transferencias_entrada', 0) or 0
                trans_saida = dados.get('transferencias_saida', 0) or 0
                if trans_entrada > 0 or trans_saida > 0:
                    trans = f"+{int(trans_entrada)}/-{int(trans_saida)}"
                else:
                    trans = "-"
                
                # Formatar evolução
                evol = dados.get('evolucao_categoria', '-') or '-'
                
                # Formatar valores monetários
                valor_unitario = float(dados.get('valor_unitario', 0) or 0)
                valor_total = float(dados.get('valor_total', 0) or 0)
                
                # Formatar valores com cores conforme a tela
                nascimentos_val = int(dados.get('nascimentos', 0) or 0)
                compras_val = int(dados.get('compras', 0) or 0)
                vendas_val = int(dados.get('vendas', 0) or 0)
                mortes_val = int(dados.get('mortes', 0) or 0)
                
                # Aplicar cores conforme a tela HTML
                nascimentos_str = f'<font color="#28a745">+{nascimentos_val}</font>' if nascimentos_val > 0 else '-'
                compras_str = f'<font color="#17a2b8">+{compras_val}</font>' if compras_val > 0 else '-'
                vendas_str = f'<font color="#dc3545">-{vendas_val}</font>' if vendas_val > 0 else '-'
                mortes_str = f'<font color="#6c757d">-{mortes_val}</font>' if mortes_val > 0 else '-'
                
                # Formatar transferências com cores
                if trans_entrada > 0 or trans_saida > 0:
                    trans_parts = []
                    if trans_entrada > 0:
                        trans_parts.append(f'<font color="#28a745">+{int(trans_entrada)}</font>')
                    if trans_saida > 0:
                        trans_parts.append(f'<font color="#dc3545">-{int(trans_saida)}</font>')
                    trans = '/'.join(trans_parts)
                else:
                    trans = '-'
                
                # Formatar evolução com cor amarela/laranja
                if evol != '-' and str(evol).strip() != '':
                    evol_str = f'<font color="#ffc107">{str(evol)}</font>'
                else:
                    evol_str = '-'
                
                table_data.append([
                    categoria,
                    str(int(dados.get('saldo_inicial', 0) or 0)),
                    nascimentos_str,
                    compras_str,
                    vendas_str,
                    mortes_str,
                    trans,
                    evol_str,
                    str(int(dados.get('saldo_final', 0) or 0)),
                    f"R$ {valor_unitario:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                ])
            
            # Adicionar linha de totais
            totais = dados_ano.get('totais', {})
            if totais:
                trans_entrada_total = totais.get('transferencias_entrada_total', 0) or 0
                trans_saida_total = totais.get('transferencias_saida_total', 0) or 0
                if trans_entrada_total > 0 or trans_saida_total > 0:
                    trans_parts = []
                    if trans_entrada_total > 0:
                        trans_parts.append(f'<font color="#28a745">+{int(trans_entrada_total)}</font>')
                    if trans_saida_total > 0:
                        trans_parts.append(f'<font color="#dc3545">-{int(trans_saida_total)}</font>')
                    trans_total = '/'.join(trans_parts)
                else:
                    trans_total = '-'
                
                valor_total_geral = float(totais.get('valor_total_geral', 0) or 0)
                
                # Formatar totais com cores
                nascimentos_total = int(totais.get('nascimentos_total', 0) or 0)
                compras_total = int(totais.get('compras_total', 0) or 0)
                vendas_total = int(totais.get('vendas_total', 0) or 0)
                mortes_total = int(totais.get('mortes_total', 0) or 0)
                
                nascimentos_total_str = f'<font color="#28a745">{nascimentos_total}</font>' if nascimentos_total > 0 else '0'
                compras_total_str = f'<font color="#17a2b8">{compras_total}</font>' if compras_total > 0 else '0'
                vendas_total_str = f'<font color="#dc3545">{vendas_total}</font>' if vendas_total > 0 else '0'
                mortes_total_str = f'<font color="#6c757d">{mortes_total}</font>' if mortes_total > 0 else '0'
                
                table_data.append([
                    '<b>TOTAL</b>',
                    str(int(totais.get('saldo_inicial_total', 0) or 0)),
                    nascimentos_total_str,
                    compras_total_str,
                    vendas_total_str,
                    mortes_total_str,
                    trans_total,
                    '-',
                    str(int(totais.get('saldo_final_total', 0) or 0)),
                    '-',
                    f"R$ {valor_total_geral:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                ])
            
            # Calcular larguras dinamicamente
            col_widths_projecao = calcular_larguras_dinamicas(table_data, 11)
            
            # Ajustar fonte baseado no conteúdo - reduzir um pouco para evitar quebra de linha
            fonte_tabela = ajustar_fonte_por_conteudo(table_data, 8)
            fonte_cabecalho = min(fonte_tabela + 1, 10)  # Limitar tamanho do cabeçalho
            
            # Dividir tabela se necessário
            tabelas_divididas = ajustar_tabela_para_pagina(table_data, col_widths_projecao)
            
            for j, parte_tabela in enumerate(tabelas_divididas):
                # Converter células com HTML para Paragraph
                parte_tabela_formatada = []
                for row_idx, row in enumerate(parte_tabela):
                    row_formatada = []
                    for col_idx, cell in enumerate(row):
                        if row_idx == 0:
                            # Cabeçalho: permitir quebra de linha com <br/> para "Saldo<br/>Inicial"
                            cell_text = str(cell)
                            # Manter <br/> para quebra de linha intencional (não remover)
                            row_formatada.append(Paragraph(cell_text, ParagraphStyle(
                                'Header',
                                fontName='Helvetica-Bold',
                                fontSize=max(8, fonte_cabecalho - 1),  # Reduzir fonte do cabeçalho
                                textColor=colors.HexColor('#1e3a8a'),
                                alignment=TA_CENTER,
                                leading=max(9, fonte_cabecalho),
                                wordWrap='CJK'  # Evitar quebra de palavras
                            )))
                        elif isinstance(cell, str) and ('<font' in cell or '<b>' in cell):
                            # Células com formatação HTML
                            # Verificar se é coluna de valor monetário (últimas 2 colunas)
                            if col_idx >= len(row) - 2:
                                # Colunas de valor: alinhar à direita
                                row_formatada.append(Paragraph(str(cell), ParagraphStyle(
                                    'Cell',
                                    fontName='Helvetica-Bold' if '<b>' in cell else 'Helvetica',
                                    fontSize=fonte_tabela,
                                    alignment=TA_LEFT if col_idx == 0 else TA_CENTER if col_idx < len(row) - 2 else TA_LEFT,
                                    leading=fonte_tabela + 1
                                )))
                            else:
                                # Outras colunas: centralizar
                                row_formatada.append(Paragraph(str(cell), ParagraphStyle(
                                    'Cell',
                                    fontName='Helvetica',
                                    fontSize=fonte_tabela,
                                    alignment=TA_CENTER,
                                    leading=fonte_tabela + 1
                                )))
                        elif isinstance(cell, str) and cell.startswith('R$'):
                            # Valores monetários sem HTML: alinhar à direita
                            row_formatada.append(Paragraph(str(cell), ParagraphStyle(
                                'Cell',
                                fontName='Helvetica-Bold' if row_idx == len(parte_tabela) - 1 else 'Helvetica',
                                fontSize=fonte_tabela,
                                alignment=TA_LEFT,
                                leading=fonte_tabela + 1
                            )))
                        else:
                            row_formatada.append(cell)
                    parte_tabela_formatada.append(row_formatada)
                
                table = Table(parte_tabela_formatada, colWidths=col_widths_projecao, repeatRows=1)
                table.setStyle(TableStyle([
                        # Cabeçalho da tabela - fundo claro como na tela (table-light)
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), max(8, fonte_cabecalho - 1)),  # Fonte menor para cabeçalho
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        ('TOPPADDING', (0, 0), (-1, 0), 6),  # Reduzir padding do cabeçalho
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        
                        # Dados da tabela
                        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -2), fonte_tabela),
                        ('FONTNAME', (0, 1), (0, -2), 'Helvetica-Bold'),  # Categoria em negrito
                        ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Categoria à esquerda
                        ('ALIGN', (1, 1), (8, -2), 'CENTER'),  # Dados centralizados (colunas 1-8)
                        ('ALIGN', (9, 1), (10, -2), 'RIGHT'),  # Valores monetários à direita (colunas 9-10)
                        ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
                        
                        # Linha de totais (apenas na última parte)
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, -1), (-1, -1), fonte_tabela + 1),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
                        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
                        ('ALIGN', (0, -1), (8, -1), 'CENTER'),  # Totais centralizados (colunas 0-8)
                        ('ALIGN', (9, -1), (9, -1), 'CENTER'),  # "-" centralizado
                        ('ALIGN', (10, -1), (10, -1), 'RIGHT'),  # Valor total à direita
                        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                        
                        # Bordas e espaçamento
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),  # Borda externa grossa
                        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),
                        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#1e3a8a')),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        
                        # Alternância de cores nas linhas
                        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
                    ]))
                
                ano_section.append(table)
                
                # Adicionar quebra de página apenas se não for a última parte da última tabela
                # Usar CondPageBreak para evitar páginas em branco
                if j < len(tabelas_divididas) - 1:
                    ano_section.append(CondPageBreak(3*cm))
            
            # Adicionar resumo financeiro do ano
            if totais:
                ano_section.append(Spacer(1, 0.4*cm))
                resumo_financeiro_style = ParagraphStyle(
                    'ResumoFinanceiro',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#1e3a8a'),
                    spaceAfter=4,
                    spaceBefore=0,
                    fontName='Helvetica-Bold'
                )
                
                receitas = float(totais.get('receitas_total', 0) or 0)
                custos = float(totais.get('custos_total', 0) or 0)  # Apenas compras
                perdas_mortes = float(totais.get('perdas_mortes', 0) or 0)  # Perdas por mortes (não são custos)
                lucro = float(totais.get('lucro_total', 0) or 0)
                
                # Formatar valores monetários
                def formatar_moeda(valor):
                    return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                # Resumo financeiro simplificado: apenas receitas e custos (compras)
                resumo_text = (
                    f"<b>Receitas:</b> R$ {formatar_moeda(receitas)} | "
                    f"<b>Custos (Compras):</b> R$ {formatar_moeda(custos)} | "
                    f"<b>Lucro:</b> R$ {formatar_moeda(lucro)}"
                )
                ano_section.append(Paragraph(resumo_text, resumo_financeiro_style))
                
                # Adicionar resumo discreto de vendas do ano
                ano_section.append(Spacer(1, 0.3*cm))
                resumo_vendas_style = ParagraphStyle(
                    'ResumoVendasStyle',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#666666'),
                    spaceAfter=2,
                    spaceBefore=0,
                    leading=10
                )
                
                # Coletar vendas por categoria
                vendas_por_categoria = []
                for ordem_sexo, idade_minima, idade_maxima, categoria_nome, dados_cat in categorias_filtradas:
                    vendas_qtd = dados_cat.get('vendas', 0) or 0
                    if vendas_qtd > 0:
                        # Calcular valor total das vendas e valor médio
                        valor_unitario = dados_cat.get('valor_unitario', 0) or 0
                        valor_total_vendas = float(vendas_qtd) * float(valor_unitario)
                        valor_medio = float(valor_unitario)
                        
                        # Formato: categoria (quantidade CBS TOTAL valor_total VLR MEDIO valor_medio)
                        # Exemplo: Bezerro(o) 0-12 M (384 CBS TOTAL R$ 930.009,60 VLR MEDIO R$ 2.424,40)
                        linha_venda = (
                            f"{categoria_nome} ({int(vendas_qtd)} CBS TOTAL R$ {formatar_moeda(valor_total_vendas)} "
                            f"VLR MEDIO R$ {formatar_moeda(valor_medio)})"
                        )
                        vendas_por_categoria.append((ordem_sexo, idade_minima, idade_maxima, linha_venda))
                
                # Ordenar vendas (fêmeas primeiro, depois machos, por idade)
                vendas_por_categoria.sort(key=lambda x: (x[0], x[1], x[2]))
                
                # Criar texto do resumo (tudo em uma linha, separado por |)
                if vendas_por_categoria:
                    linhas_vendas = [v[3] for v in vendas_por_categoria]
                    resumo_vendas_texto = " | ".join(linhas_vendas)
                    ano_section.append(Paragraph(f"<b>RESUMO DE VENDAS:</b> {resumo_vendas_texto}", resumo_vendas_style))
            
            # Adicionar seção do ano sem KeepTogether completo (pode causar páginas em branco)
            # Adicionar elementos individualmente
            for elemento in ano_section:
                story.append(elemento)
            
            # Quebra de página após cada ano (exceto o último) - usar CondPageBreak
            if ano != max(resumo_projecao_por_ano.keys()):
                story.append(CondPageBreak(3*cm))
    
    # Gráfico de Evolução do Rebanho - SEMPRE DEPOIS DO ÚLTIMO ANO PROJETADO
    if grafico_bytes:
        # Quebra de página condicional antes do gráfico
        story.append(CondPageBreak(10*cm))  # Quebra apenas se não houver espaço suficiente
        story.append(Paragraph("EVOLUÇÃO DO REBANHO", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Adicionar gráfico
        try:
            img = Image(grafico_bytes, width=16*cm, height=8*cm)
            story.append(img)
            story.append(Spacer(1, 0.5*cm))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao adicionar gráfico ao PDF: {e}")
            story.append(Paragraph("Gráfico de evolução não disponível.", normal_style))
            story.append(Spacer(1, 0.3*cm))
    
    # Análise Financeira
    # Adicionar quebra de página apenas se houver projeções (para separar do gráfico ou último ano)
    # Usar CondPageBreak para evitar página em branco se houver espaço suficiente
    if resumo_projecao_por_ano:
        story.append(CondPageBreak(6*cm))  # Quebra apenas se não houver espaço suficiente
    story.append(Paragraph("2. ANÁLISE FINANCEIRA", section_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Calcular receitas e despesas por ano
    analise_financeira_data = [['Ano', 'Receitas (R$)', 'Despesas (R$)', 'Lucro (R$)', 'Margem (%)', 'ROI (%)']]
    
    receita_total_periodo = 0
    despesa_total_periodo = 0
    
    for ano, dados_ano in sorted(resumo_projecao_por_ano.items()):
        # Usar estrutura correta: dados_ano['totais']
        totais_ano = dados_ano.get('totais', {})
        receitas_ano = float(totais_ano.get('receitas_total', 0) or 0)
        despesas_ano = float(totais_ano.get('custos_total', 0) or 0)
        lucro_ano = float(totais_ano.get('lucro_total', 0) or 0)
        margem_ano = (lucro_ano / receitas_ano * 100) if receitas_ano > 0 else 0
        roi_ano = (lucro_ano / valor_total_rebanho * 100) if valor_total_rebanho > 0 else 0
        
        receita_total_periodo += receitas_ano
        despesa_total_periodo += despesas_ano
        
        analise_financeira_data.append([
            str(ano),
            f"R$ {receitas_ano:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"R$ {despesas_ano:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"R$ {lucro_ano:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"{margem_ano:.1f}%",
            f"{roi_ano:.1f}%"
        ])
    
    # Adicionar linha de totais
    lucro_total = receita_total_periodo - despesa_total_periodo
    margem_total = (lucro_total / receita_total_periodo * 100) if receita_total_periodo > 0 else 0
    roi_total = (lucro_total / valor_total_rebanho * 100) if valor_total_rebanho > 0 else 0
    
    analise_financeira_data.append([
        'TOTAL PERÍODO',
        f"R$ {receita_total_periodo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"R$ {despesa_total_periodo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"R$ {lucro_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"{margem_total:.1f}%",
        f"{roi_total:.1f}%"
    ])
    
    analise_table = Table(analise_financeira_data, colWidths=[3.5*cm, 5.5*cm, 5.5*cm, 5.5*cm, 3.5*cm, 3.5*cm])
    analise_table.setStyle(TableStyle([
        # Cabeçalho da tabela
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Dados da tabela
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 11),
        ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # Ano centralizado
        ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),  # Valores à direita
        ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
        
        # Linha de totais
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
        
        # Bordas e espaçamento
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),  # Borda externa grossa
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        # Alternância de cores nas linhas
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(analise_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Resumo dos indicadores de rentabilidade
    story.append(Paragraph("INDICADORES DE RENTABILIDADE", subsection_style))
    story.append(Spacer(1, 0.2*cm))
    
    indicadores_rentabilidade_data = [
        ['Indicador', 'Valor', 'Interpretação'],
        ['Margem Bruta Média', f"{margem_total:.1f}%", 'Excelente' if margem_total > 20 else 'Boa' if margem_total > 10 else 'Regular' if margem_total > 0 else 'Negativa'],
        ['ROI Médio', f"{roi_total:.1f}%", 'Excelente' if roi_total > 15 else 'Bom' if roi_total > 8 else 'Regular' if roi_total > 0 else 'Negativo'],
        ['Receita Total Projetada', f"R$ {receita_total_periodo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), f"Em {len(resumo_projecao_por_ano)} anos"],
        ['Lucro Total Projetado', f"R$ {lucro_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), f"Período {min(resumo_projecao_por_ano.keys())}-{max(resumo_projecao_por_ano.keys())}"],
    ]
    
    indicadores_table = Table(indicadores_rentabilidade_data, colWidths=[7*cm, 5*cm, 7*cm])
    indicadores_table.setStyle(TableStyle([
        # Cabeçalho da tabela
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6495ed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Dados da tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Indicador à esquerda
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Valor à direita
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Interpretação à esquerda
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Bordas e espaçamento
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#6495ed')),  # Borda externa grossa
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#6495ed')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        # Alternância de cores nas linhas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(indicadores_table)
    story.append(PageBreak())
    
    # Função para adicionar rodapé com numeração
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        
        # Rodapé esquerdo - Propriedade
        canvas.drawString(1*cm, 0.5*cm, f"Propriedade: {propriedade.nome_propriedade}")
        
        # Rodapé direito - Data e página
        canvas.drawRightString(28.7*cm, 0.5*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(28.7*cm, 0.2*cm, f"Página {doc.page}")
        
        canvas.restoreState()
    
    # Construir PDF com rodapé
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return response


@login_required
def exportar_iatf_excel(request, propriedade_id):
    """Exporta o relatório completo de IATF em formato Excel."""
    from .models import Propriedade

    propriedade = get_object_or_404(
        Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user
    )

    filtros = {
        'data_inicio': request.GET.get('data_inicio'),
        'data_final': request.GET.get('data_final'),
        'diagnostico_ate': request.GET.get('diagnostico_ate'),
        'lote_id': request.GET.get('lote_id'),
        'resultado': request.GET.get('resultado'),
    }

    try:
        dados = coletar_dados_iatf(propriedade, filtros)
    except IATFModuloIndisponivel as exc:
        return HttpResponse(str(exc), status=400, content_type='text/plain; charset=utf-8')

    resumo = dados['resumo']
    filtros_aplicados = dados['filtros_aplicados']

    def _to_float(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _aplicar_header(cells):
        for cell in cells:
            cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal='center', vertical='center')

    def _escrever_tabela(ws, headers, linhas):
        ws.append(headers)
        _aplicar_header(ws[ws.max_row])
        for linha in linhas:
            ws.append(linha)

    wb = Workbook()
    ws_resumo = wb.active
    ws_resumo.title = "Resumo"

    ws_resumo['A1'] = "Relatório detalhado de IATF"
    ws_resumo['A1'].font = Font(bold=True, size=16)
    ws_resumo['A2'] = "Propriedade"
    ws_resumo['B2'] = getattr(propriedade, 'nome_propriedade', str(propriedade))
    ws_resumo['A3'] = "Gerado em"
    ws_resumo['B3'] = datetime.now().strftime('%d/%m/%Y %H:%M')

    filtros_texto = []
    if filtros_aplicados.get('data_inicio'):
        filtros_texto.append(f"IATF ≥ {filtros_aplicados['data_inicio'].strftime('%d/%m/%Y')}")
    if filtros_aplicados.get('data_final'):
        filtros_texto.append(f"IATF ≤ {filtros_aplicados['data_final'].strftime('%d/%m/%Y')}")
    if filtros_aplicados.get('diagnostico_ate'):
        filtros_texto.append(f"Diagnóstico ≤ {filtros_aplicados['diagnostico_ate'].strftime('%d/%m/%Y')}")
    if filtros_aplicados.get('lote_id'):
        filtros_texto.append(f"Lote #{filtros_aplicados['lote_id']}")
    if filtros_aplicados.get('resultado'):
        filtros_texto.append(f"Resultado = {filtros_aplicados['resultado']}")

    ws_resumo['A4'] = "Filtros"
    ws_resumo['B4'] = ', '.join(filtros_texto) if filtros_texto else 'Sem filtros adicionais'

    ws_resumo.append([])
    ws_resumo.append(['Indicador', 'Valor'])
    _aplicar_header(ws_resumo[ws_resumo.max_row])

    metricas = [
        ("Total de IATFs avaliadas", resumo['total_animais']),
        ("Prenhezes confirmadas", resumo['total_prenhezes']),
        ("Taxa de prenhez (%)", _to_float(resumo['taxa_prenhez'])),
        ("Vazias", resumo['total_vazias']),
        ("Abortos", resumo['total_abortos']),
        ("Repetições de cio", resumo['total_repeticoes']),
        ("Diagnósticos pendentes", resumo['total_pendentes']),
        ("Dias médios até diagnóstico", _to_float(resumo['media_dias_diagnostico'])),
        ("Custo total (R$)", _to_float(resumo['custo_total'])),
        ("Custo médio por animal (R$)", _to_float(resumo['custo_medio_animal'])),
        ("Custo médio por prenhez (R$)", _to_float(resumo['custo_medio_prenhez'])),
    ]
    for label, valor in metricas:
        ws_resumo.append([label, valor if valor is not None else '-'])

    for row in ws_resumo.iter_rows(min_row=7, min_col=2, max_col=2, max_row=ws_resumo.max_row):
        celula = row[0]
        if isinstance(celula.value, (int, float)):
            indicador = ws_resumo[f"A{celula.row}"].value or ''
            if 'Custo' in indicador:
                celula.number_format = 'R$ #,##0.00'
            elif 'Taxa' in indicador:
                celula.number_format = '0.00'
            elif 'Dias' in indicador:
                celula.number_format = '0.00'

    ws_resumo.append([])
    ws_resumo.append(['Resultados', 'Quantidade', 'Taxa (%)'])
    _aplicar_header(ws_resumo[ws_resumo.max_row])
    for item in dados['status_counts']:
        ws_resumo.append([
            item['rotulo'],
            item['total'],
            _to_float(item['taxa']),
        ])
    for row in ws_resumo.iter_rows(
        min_row=ws_resumo.max_row - len(dados['status_counts']) + 1,
        min_col=3,
        max_col=3,
        max_row=ws_resumo.max_row,
    ):
        row[0].number_format = '0.00'

    ws_resumo.column_dimensions['A'].width = 42
    ws_resumo.column_dimensions['B'].width = 28
    ws_resumo.freeze_panes = 'A7'

    def _planilha_agrupamento(nome, dados_agrupados, incluir_custos=True):
        ws = wb.create_sheet(nome)
        headers = [
            nome.split(' ', 1)[-1],
            'Total',
            'Prenhezes',
            'Taxa Prenhez (%)',
            'Vazias',
            'Abortos',
            'Repetições',
            'Dias médios diagnóstico',
        ]
        if incluir_custos:
            headers.append('Custo médio/prenhez (R$)')

        linhas = []
        for item in dados_agrupados:
            linha = [
                item['rotulo'],
                item['total'],
                item['prenhezes'],
                _to_float(item['taxa_prenhez']),
                item['vazias'],
                item['abortos'],
                item['repeticoes'],
                _to_float(item['media_dias_diagnostico']),
            ]
            if incluir_custos:
                linha.append(_to_float(item['custo_medio_prenhez']))
            linhas.append(linha)

        _escrever_tabela(ws, headers, linhas)

        if linhas:
            ws.freeze_panes = 'A2'
            ws.column_dimensions['A'].width = 32
            for col in range(2, ws.max_column + 1):
                ws.column_dimensions[chr(64 + col)].width = 18
            ws.auto_filter.ref = ws.dimensions
            taxa_col = 4
            dias_col = 8
            custo_col = 9 if incluir_custos else None
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                if _to_float(row[taxa_col - 1].value) is not None:
                    row[taxa_col - 1].number_format = '0.00'
                if _to_float(row[dias_col - 1].value) is not None:
                    row[dias_col - 1].number_format = '0.00'
                if custo_col and _to_float(row[custo_col - 1].value) is not None:
                    row[custo_col - 1].number_format = 'R$ #,##0.00'

            if nome == "Por Touro" and len(linhas) >= 1:
                chart = BarChart()
                chart.title = "Prenhezes por touro"
                data_ref = Reference(ws, min_col=3, min_row=1, max_row=len(linhas) + 1)
                categories_ref = Reference(ws, min_col=1, min_row=2, max_row=len(linhas) + 1)
                chart.add_data(data_ref, titles_from_data=True)
                chart.set_categories(categories_ref)
                chart.y_axis.title = "Prenhezes"
                chart.x_axis.title = "Touros"
                ws.add_chart(chart, f'{chr(65 + ws.max_column + 1)}2')

    _planilha_agrupamento("Por Touro", dados['por_touro'])
    _planilha_agrupamento("Por Inseminador", dados['por_inseminador'])
    _planilha_agrupamento("Por Invernada", dados['por_invernada'], incluir_custos=False)
    _planilha_agrupamento("Por Lote", dados['por_lote'])
    _planilha_agrupamento("Por Protocolo", dados['por_protocolo'])

    ws_diagnosticos = wb.create_sheet("Diagnosticos")
    linhas_diagnosticos = [
        [
            item['data_diagnostico'],
            item['total'],
            item['prenhezes'],
            _to_float(item['taxa_prenhez']),
            item['vazias'],
        ]
        for item in dados['diagnosticos_por_data']
    ]
    _escrever_tabela(
        ws_diagnosticos,
        ['Data do diagnóstico', 'Total', 'Prenhezes', 'Taxa Prenhez (%)', 'Vazias'],
        linhas_diagnosticos,
    )
    if linhas_diagnosticos:
        ws_diagnosticos.freeze_panes = 'A2'
        ws_diagnosticos.column_dimensions['A'].width = 18
        for row in ws_diagnosticos.iter_rows(min_row=2, min_col=4, max_col=4, max_row=ws_diagnosticos.max_row):
            row[0].number_format = '0.00'

    ws_detalhes = wb.create_sheet("Detalhes")
    ws_detalhes.append([
        'Animal',
        'Categoria',
        'Invernada',
        'Protocolo',
        'Lote IATF',
        'Touro',
        'Inseminador',
        'Resultado',
        'Status',
        'Data IATF',
        'Data diagnóstico',
        'Dias até diagnóstico',
        'Custo total (R$)',
        'Observações',
    ])
    _aplicar_header(ws_detalhes[1])

    for item in dados['detalhes']:
        ws_detalhes.append([
            item['animal'],
            item['categoria'],
            item['invernada'],
            item['protocolo'],
            item['lote_iatf'],
            item['touro'],
            item['inseminador'],
            item['resultado'],
            item['status'],
            item['data_iatf'],
            item['data_diagnostico'],
            item['dias_para_diagnostico'],
            _to_float(item['custo_total']),
            item['observacoes'],
        ])

    ws_detalhes.freeze_panes = 'A2'
    col_widths = {
        'A': 16,
        'B': 20,
        'C': 24,
        'D': 22,
        'E': 22,
        'F': 26,
        'G': 22,
        'H': 18,
        'I': 18,
        'J': 14,
        'K': 18,
        'L': 18,
        'M': 18,
        'N': 48,
    }
    for coluna, largura in col_widths.items():
        ws_detalhes.column_dimensions[coluna].width = largura
    for row in ws_detalhes.iter_rows(min_row=2, min_col=13, max_col=13, max_row=ws_detalhes.max_row):
        row[0].number_format = 'R$ #,##0.00'

    nome_arquivo = f"iatf_{propriedade.id}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    wb.save(response)
    return response


@login_required
def exportar_iatf_pdf(request, propriedade_id):
    """Exporta o relatório completo de IATF em PDF com tabelas analíticas."""
    from .models import Propriedade

    propriedade = get_object_or_404(
        Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user
    )

    filtros = {
        'data_inicio': request.GET.get('data_inicio'),
        'data_final': request.GET.get('data_final'),
        'diagnostico_ate': request.GET.get('diagnostico_ate'),
        'lote_id': request.GET.get('lote_id'),
        'resultado': request.GET.get('resultado'),
    }

    try:
        dados = coletar_dados_iatf(propriedade, filtros)
    except IATFModuloIndisponivel as exc:
        return HttpResponse(str(exc), status=400, content_type='text/plain; charset=utf-8')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="iatf_{propriedade.id}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'IATFTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    subtitle_style = ParagraphStyle(
        'IATFSubtitle',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#4a5568'),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    section_style = ParagraphStyle(
        'IATFSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=8,
        spaceBefore=12,
    )

    def format_percent(valor):
        if valor is None:
            return '-'
        return f"{float(valor):.2f}%".replace('.', ',')

    def format_decimal(valor, casas=2):
        if valor is None:
            return '-'
        return f"{float(valor):.{casas}f}".replace('.', ',')

    def format_currency(valor):
        if valor is None:
            return '-'
        texto = f"{float(valor):,.2f}"
        texto = texto.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"R$ {texto}"

    def format_date(valor):
        if not valor:
            return '-'
        return valor.strftime('%d/%m/%Y')

    story = []
    story.append(Paragraph("Relatório detalhado de IATF", title_style))
    story.append(Paragraph(getattr(propriedade, 'nome_propriedade', str(propriedade)), subtitle_style))
    story.append(Paragraph(datetime.now().strftime('%d/%m/%Y %H:%M'), subtitle_style))

    filtros_aplicados = dados['filtros_aplicados']
    filtros_texto = []
    if filtros_aplicados.get('data_inicio'):
        filtros_texto.append(f"IATFs a partir de {format_date(filtros_aplicados['data_inicio'])}")
    if filtros_aplicados.get('data_final'):
        filtros_texto.append(f"IATFs até {format_date(filtros_aplicados['data_final'])}")
    if filtros_aplicados.get('diagnostico_ate'):
        filtros_texto.append(f"Diagnóstico até {format_date(filtros_aplicados['diagnostico_ate'])}")
    if filtros_aplicados.get('resultado'):
        filtros_texto.append(f"Resultado filtrado: {filtros_aplicados['resultado']}")
    if filtros_aplicados.get('lote_id'):
        filtros_texto.append(f"Lote específico #{filtros_aplicados['lote_id']}")

    if filtros_texto:
        story.append(Paragraph(' | '.join(filtros_texto), ParagraphStyle(
            'Filtros',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
            spaceAfter=12,
        )))

    resumo = dados['resumo']
    tabela_resumo = [
        ['Indicador', 'Valor'],
        ['Total de IATFs avaliadas', resumo['total_animais']],
        ['Prenhezes confirmadas', resumo['total_prenhezes']],
        ['Taxa de prenhez', format_percent(resumo['taxa_prenhez'])],
        ['Vazias', resumo['total_vazias']],
        ['Abortos', resumo['total_abortos']],
        ['Repetições de cio', resumo['total_repeticoes']],
        ['Diagnósticos pendentes', resumo['total_pendentes']],
        ['Dias médios até diagnóstico', format_decimal(resumo['media_dias_diagnostico'])],
        ['Custo total', format_currency(resumo['custo_total'])],
        ['Custo médio por animal', format_currency(resumo['custo_medio_animal'])],
        ['Custo médio por prenhez', format_currency(resumo['custo_medio_prenhez'])],
    ]
    tabela_resumo_obj = Table(tabela_resumo, colWidths=[9 * cm, 7 * cm], hAlign='LEFT')
    tabela_resumo_obj.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CBD5F5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tabela_resumo_obj)
    story.append(Spacer(1, 0.4 * cm))

    if dados['status_counts']:
        story.append(Paragraph("Distribuição por resultado", section_style))
        tabela_status = [['Resultado', 'Quantidade', 'Taxa']]
        for item in dados['status_counts']:
            tabela_status.append([
                item['rotulo'],
                item['total'],
                format_percent(item['taxa']),
            ])
        tabela_status_obj = Table(tabela_status, hAlign='LEFT')
        tabela_status_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CBD5F5')),
        ]))
        story.append(tabela_status_obj)
        story.append(Spacer(1, 0.4 * cm))

    def _adicionar_secao_tabela(titulo, dados_agrupados, incluir_custos=True):
        if not dados_agrupados:
            return
        story.append(Paragraph(titulo, section_style))
        headers = [
            titulo.split(' ', 1)[-1],
            'Total',
            'Prenhezes',
            'Taxa',
            'Vazias',
            'Abortos',
            'Repetições',
            'Dias médios',
        ]
        if incluir_custos:
            headers.append('Custo médio/prenhez')
        tabela = [headers]
        for item in dados_agrupados:
            linha = [
                item['rotulo'],
                item['total'],
                item['prenhezes'],
                format_percent(item['taxa_prenhez']),
                item['vazias'],
                item['abortos'],
                item['repeticoes'],
                format_decimal(item['media_dias_diagnostico']),
            ]
            if incluir_custos:
                linha.append(format_currency(item['custo_medio_prenhez']))
            tabela.append(linha)

        colunas = len(headers)
        largura_base = [6.5 * cm] + [2.3 * cm] * (colunas - 1)
        tabela_obj = Table(tabela, colWidths=largura_base, repeatRows=1, hAlign='LEFT')
        tabela_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CBD5F5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tabela_obj)
        story.append(Spacer(1, 0.3 * cm))

    _adicionar_secao_tabela("Desempenho por touro", dados['por_touro'])
    _adicionar_secao_tabela("Desempenho por inseminador", dados['por_inseminador'])
    _adicionar_secao_tabela("Desempenho por invernada", dados['por_invernada'], incluir_custos=False)
    _adicionar_secao_tabela("Desempenho por lote", dados['por_lote'])
    _adicionar_secao_tabela("Desempenho por protocolo", dados['por_protocolo'])

    if dados['diagnosticos_por_data']:
        story.append(Paragraph("Diagnósticos ao longo do tempo", section_style))
        tabela_diag = [['Data', 'Total', 'Prenhezes', 'Taxa', 'Vazias']]
        for item in dados['diagnosticos_por_data']:
            tabela_diag.append([
                format_date(item['data_diagnostico']),
                item['total'],
                item['prenhezes'],
                format_percent(item['taxa_prenhez']),
                item['vazias'],
            ])
        tabela_diag_obj = Table(tabela_diag, repeatRows=1, hAlign='LEFT')
        tabela_diag_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CBD5F5')),
        ]))
        story.append(tabela_diag_obj)
        story.append(Spacer(1, 0.3 * cm))

    detalhes = dados['detalhes']
    if detalhes:
        story.append(Paragraph("Detalhamento por animal", section_style))
        limite = 40
        if len(detalhes) > limite:
            aviso = Paragraph(
                f"Mostrando {limite} de {len(detalhes)} registros. Utilize a exportação Excel para obter a lista completa.",
                ParagraphStyle('Aviso', parent=styles['Italic'], textColor=colors.HexColor('#718096'), spaceAfter=6),
            )
            story.append(aviso)
        tabela_detalhes = [['Animal', 'Resultado', 'Touro', 'Lote', 'Diagnóstico', 'Dias', 'Custo', 'Observações']]
        for item in detalhes[:limite]:
            tabela_detalhes.append([
                item['animal'],
                item['resultado'],
                item['touro'],
                item['lote_iatf'],
                format_date(item['data_diagnostico']),
                item['dias_para_diagnostico'] if item['dias_para_diagnostico'] is not None else '-',
                format_currency(item['custo_total']),
                (item['observacoes'] or '')[:160],
            ])
        tabela_detalhes_obj = Table(
            tabela_detalhes,
            colWidths=[3.2 * cm, 3 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 1.8 * cm, 3 * cm, 5 * cm],
            repeatRows=1,
            hAlign='LEFT',
        )
        tabela_detalhes_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-2, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CBD5F5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tabela_detalhes_obj)

    doc.build(story)
    return response


@login_required
def exportar_inventario_pdf(request, propriedade_id):
    """Exporta inventário para PDF com cabeçalho formatado"""
    from .models import InventarioRebanho, Propriedade
    from datetime import datetime
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar inventário mais recente
    inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').order_by('-data_inventario').first()
    
    if not inventario_recente:
        from django.contrib import messages
        messages.warning(request, 'Nenhum inventário encontrado para exportar.')
        from django.shortcuts import redirect
        return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    data_inventario = inventario_recente.data_inventario
    
    # Buscar todos os itens do inventário na mesma data
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario=data_inventario
    ).select_related('categoria').order_by('categoria__sexo', 'categoria__idade_minima_meses')
    
    # Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    nome_arquivo = f'inventario_{propriedade.nome_propriedade.replace(" ", "_")}_{data_inventario.strftime("%Y%m%d")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    
    # Criar documento PDF em formato paisagem
    doc = SimpleDocTemplate(response, pagesize=landscape(A4), 
                           rightMargin=1.5*cm, leftMargin=1.5*cm,
                           topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Cores
    azul_escuro = colors.HexColor('#1e3a5f')
    azul_medio = colors.HexColor('#366092')
    verde_claro = colors.HexColor('#d4edda')
    cinza_claro = colors.HexColor('#f2f2f2')
    
    # Estilo do título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.white,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=azul_escuro,
        leading=24
    )
    
    # Estilo do subtítulo
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica',
        backColor=azul_medio,
        leading=18
    )
    
    # Estilo da informação
    info_style = ParagraphStyle(
        'CustomInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.white,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica',
        backColor=azul_medio,
        leading=14
    )
    
    # ===== CABEÇALHO =====
    # Título principal com fundo (ajustado para paisagem)
    largura_pagina = landscape(A4)[0] - 3*cm  # Largura total menos margens
    titulo_box = Table(
        [[Paragraph('RELATÓRIO DE INVENTÁRIO DO REBANHO', title_style)]],
        colWidths=[largura_pagina],
        rowHeights=[1.2*cm]
    )
    titulo_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), azul_escuro),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
    ]))
    story.append(titulo_box)
    
    # Informações da propriedade
    propriedade_box = Table(
        [[Paragraph(f'Propriedade: {propriedade.nome_propriedade}', subtitle_style)]],
        colWidths=[largura_pagina],
        rowHeights=[0.8*cm]
    )
    propriedade_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), azul_medio),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
    ]))
    story.append(propriedade_box)
    
    # Localização e data
    localizacao = f'{propriedade.municipio}/{propriedade.uf}' if propriedade.municipio else ''
    info_texto = f'{localizacao} | Data do Inventário: {data_inventario.strftime("%d/%m/%Y")} | Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    info_box = Table(
        [[Paragraph(info_texto, info_style)]],
        colWidths=[largura_pagina],
        rowHeights=[0.6*cm]
    )
    info_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), azul_medio),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
    ]))
    story.append(info_box)
    
    story.append(Spacer(1, 0.5*cm))
    
    # ===== TABELA DE INVENTÁRIO =====
    # Cabeçalho da tabela
    headers = ['Categoria', 'Idade', 'Sexo', 'Quantidade', 'Valor por Cabeça (R$)', 'Valor Total (R$)']
    table_data = [headers]
    
    total_quantidade = 0
    total_valor = Decimal('0.00')
    
    # Separar por sexo
    femeas = []
    machos = []
    
    for item in inventario:
        if item.categoria.sexo == 'F':
            femeas.append(item)
        elif item.categoria.sexo == 'M':
            machos.append(item)
        else:
            femeas.append(item)  # Default
    
    # Fêmeas primeiro
    for item in femeas:
        idade_str = ''
        if item.categoria.idade_minima_meses is not None and item.categoria.idade_maxima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}-{item.categoria.idade_maxima_meses} M'
        elif item.categoria.idade_minima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}+ M'
        elif item.categoria.idade_maxima_meses is not None:
            idade_str = f'Até {item.categoria.idade_maxima_meses} M'
        
        sexo_str = item.categoria.get_sexo_display() if hasattr(item.categoria, 'get_sexo_display') else ('Fêmea' if item.categoria.sexo == 'F' else 'Macho')
        
        valor_total = float(item.valor_total) if item.valor_total else 0.0
        total_quantidade += item.quantidade
        total_valor += Decimal(str(valor_total))
        
        table_data.append([
            item.categoria.nome,
            idade_str,
            sexo_str,
            str(item.quantidade),
            f"R$ {float(item.valor_por_cabeca):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
    
    # Machos
    for item in machos:
        idade_str = ''
        if item.categoria.idade_minima_meses is not None and item.categoria.idade_maxima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}-{item.categoria.idade_maxima_meses} M'
        elif item.categoria.idade_minima_meses is not None:
            idade_str = f'{item.categoria.idade_minima_meses}+ M'
        elif item.categoria.idade_maxima_meses is not None:
            idade_str = f'Até {item.categoria.idade_maxima_meses} M'
        
        sexo_str = item.categoria.get_sexo_display() if hasattr(item.categoria, 'get_sexo_display') else ('Fêmea' if item.categoria.sexo == 'F' else 'Macho')
        
        valor_total = float(item.valor_total) if item.valor_total else 0.0
        total_quantidade += item.quantidade
        total_valor += Decimal(str(valor_total))
        
        table_data.append([
            item.categoria.nome,
            idade_str,
            sexo_str,
            str(item.quantidade),
            f"R$ {float(item.valor_por_cabeca):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
    
    # Linha de totais
    total_valor_float = float(total_valor)
    total_valor_formatado = f"R$ {total_valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    table_data.append(['TOTAIS', '-', '-', str(total_quantidade), '-', total_valor_formatado])
    
    # Criar tabela (ajustada para paisagem - colunas mais largas)
    # Largura total disponível menos margens
    largura_disponivel = landscape(A4)[0] - 3*cm
    # Distribuir largura proporcionalmente
    col_widths = [
        6*cm,      # Categoria (mais larga)
        2.5*cm,    # Idade
        2*cm,      # Sexo
        2.5*cm,    # Quantidade
        3.5*cm,    # Valor por Cabeça
        3.5*cm     # Valor Total
    ]
    # Ajustar se necessário para caber na página
    soma_larguras = sum(col_widths)
    if soma_larguras > largura_disponivel:
        fator = largura_disponivel / soma_larguras
        col_widths = [w * fator for w in col_widths]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilizar tabela
    table_style = [
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), azul_medio),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Dados - linhas alternadas
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Categoria alinhada à esquerda
        ('ALIGN', (1, 1), (-1, -2), 'CENTER'),  # Resto centralizado
        ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, cinza_claro]),
        
        # Linha de totais
        ('BACKGROUND', (0, -1), (-1, -1), verde_claro),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('ALIGN', (0, -1), (0, -1), 'LEFT'),
        ('ALIGN', (1, -1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#28a745')),
    ]
    
    table.setStyle(TableStyle(table_style))
    story.append(table)
    
    # Construir PDF
    doc.build(story)
    return response

