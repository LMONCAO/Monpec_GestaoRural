# -*- coding: utf-8 -*-
"""
Script para converter o estudo de rastreabilidade bovina de Markdown para PDF
"""

import re
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def processar_markdown_para_pdf(md_path: Path, pdf_path: Path):
    """Converte arquivo Markdown para PDF formatado"""
    
    # Ler conteúdo do Markdown
    conteudo = md_path.read_text(encoding='utf-8')
    linhas = conteudo.splitlines()
    
    # Configurar estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    styles.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        spaceAfter=20,
        textColor=colors.HexColor('#1e88e5'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='TituloSecao',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#1565c0'),
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='TituloSubSecao',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.HexColor('#1976d2'),
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='TituloSubSubSecao',
        parent=styles['Heading3'],
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor('#42a5f5'),
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='TextoNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='TextoNegrito',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='ListaItem',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        leftIndent=20,
        spaceAfter=4,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='TabelaCabecalho',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        backColor=colors.HexColor('#1e88e5'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='TabelaCelula',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName='Helvetica',
        alignment=TA_LEFT
    ))
    
    # Criar documento PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    story = []
    
    # Processar linhas do Markdown
    i = 0
    em_lista = False
    lista_itens = []
    em_tabela = False
    tabela_linhas = []
    tabela_cabecalho = None
    
    while i < len(linhas):
        linha = linhas[i].strip()
        
        # Pular linhas vazias (mas manter espaçamento)
        if not linha:
            if em_lista and lista_itens:
                # Finalizar lista
                for item in lista_itens:
                    story.append(Paragraph(f"• {item}", styles['ListaItem']))
                lista_itens = []
                em_lista = False
            elif em_tabela and tabela_linhas:
                # Finalizar tabela
                if tabela_cabecalho:
                    dados_tabela = [tabela_cabecalho] + tabela_linhas
                else:
                    dados_tabela = tabela_linhas
                
                if dados_tabela:
                    # Calcular larguras das colunas
                    num_cols = len(dados_tabela[0])
                    largura_col = (A4[0] - 4*cm) / num_cols
                    larguras = [largura_col] * num_cols
                    
                    # Criar tabela
                    tabela = Table(dados_tabela, colWidths=larguras)
                    tabela.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('TOPPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 1), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ]))
                    story.append(Spacer(1, 0.3*cm))
                    story.append(tabela)
                    story.append(Spacer(1, 0.5*cm))
                
                tabela_linhas = []
                tabela_cabecalho = None
                em_tabela = False
            
            story.append(Spacer(1, 0.3*cm))
            i += 1
            continue
        
        # Detectar tabelas (linhas com |)
        if '|' in linha and linha.count('|') >= 2:
            if not em_tabela:
                em_tabela = True
                tabela_linhas = []
                tabela_cabecalho = None
            
            # Pular linha de separação (---)
            if re.match(r'^\|[\s\-\|:]+\|$', linha):
                i += 1
                continue
            
            # Processar linha da tabela
            celulas = [c.strip() for c in linha.split('|') if c.strip()]
            if celulas:
                # Primeira linha com dados é o cabeçalho
                if tabela_cabecalho is None:
                    tabela_cabecalho = celulas
                else:
                    tabela_linhas.append(celulas)
            
            i += 1
            continue
        
        # Se estava em tabela, finalizar
        if em_tabela:
            em_tabela = False
            if tabela_cabecalho and tabela_linhas:
                dados_tabela = [tabela_cabecalho] + tabela_linhas
                num_cols = len(dados_tabela[0])
                largura_col = (A4[0] - 4*cm) / num_cols
                larguras = [largura_col] * num_cols
                
                tabela = Table(dados_tabela, colWidths=larguras)
                tabela.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                story.append(Spacer(1, 0.3*cm))
                story.append(tabela)
                story.append(Spacer(1, 0.5*cm))
            
            tabela_linhas = []
            tabela_cabecalho = None
        
        # Título principal (# Título)
        if linha.startswith('# '):
            texto = linha[2:].strip()
            # Remover emojis e caracteres especiais para título
            texto = re.sub(r'[📋🔍✅⚠️❌]', '', texto).strip()
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(texto, styles['TituloPrincipal']))
            story.append(Spacer(1, 0.3*cm))
            i += 1
            continue
        
        # Título de seção (## Seção)
        if linha.startswith('## '):
            texto = linha[3:].strip()
            texto = re.sub(r'[📋🔍✅⚠️❌]', '', texto).strip()
            story.append(Spacer(1, 0.4*cm))
            story.append(Paragraph(texto, styles['TituloSecao']))
            i += 1
            continue
        
        # Título de subseção (### Subseção)
        if linha.startswith('### '):
            texto = linha[4:].strip()
            texto = re.sub(r'[📋🔍✅⚠️❌]', '', texto).strip()
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(texto, styles['TituloSubSecao']))
            i += 1
            continue
        
        # Título de sub-subseção (#### Sub-subseção)
        if linha.startswith('#### '):
            texto = linha[5:].strip()
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(texto, styles['TituloSubSubSecao']))
            i += 1
            continue
        
        # Separador (---)
        if linha.startswith('---'):
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph('_' * 80, styles['TextoNormal']))
            story.append(Spacer(1, 0.5*cm))
            i += 1
            continue
        
        # Lista (- item ou * item)
        if linha.startswith('- ') or linha.startswith('* '):
            item = linha[2:].strip()
            # Processar negrito e itálico
            item = processar_formatacao(item)
            lista_itens.append(item)
            em_lista = True
            i += 1
            continue
        
        # Lista numerada (1. item)
        if re.match(r'^\d+\.\s', linha):
            item = re.sub(r'^\d+\.\s', '', linha).strip()
            item = processar_formatacao(item)
            lista_itens.append(item)
            em_lista = True
            i += 1
            continue
        
        # Se estava em lista, finalizar
        if em_lista and lista_itens:
            for item in lista_itens:
                story.append(Paragraph(f"• {item}", styles['ListaItem']))
            lista_itens = []
            em_lista = False
        
        # Texto normal
        if linha:
            texto = processar_formatacao(linha)
            story.append(Paragraph(texto, styles['TextoNormal']))
        
        i += 1
    
    # Finalizar lista pendente
    if em_lista and lista_itens:
        for item in lista_itens:
            story.append(Paragraph(f"• {item}", styles['ListaItem']))
    
    # Finalizar tabela pendente
    if em_tabela and tabela_cabecalho and tabela_linhas:
        dados_tabela = [tabela_cabecalho] + tabela_linhas
        num_cols = len(dados_tabela[0])
        largura_col = (A4[0] - 4*cm) / num_cols
        larguras = [largura_col] * num_cols
        
        tabela = Table(dados_tabela, colWidths=larguras)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        story.append(Spacer(1, 0.3*cm))
        story.append(tabela)
    
    # Construir PDF
    doc.build(story)
    print(f"✅ PDF gerado com sucesso: {pdf_path}")


def processar_formatacao(texto: str) -> str:
    """Processa formatação Markdown para HTML compatível com ReportLab"""
    # Negrito **texto** ou __texto__
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    texto = re.sub(r'__(.*?)__', r'<b>\1</b>', texto)
    
    # Itálico *texto* ou _texto_
    texto = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', texto)
    texto = re.sub(r'(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)', r'<i>\1</i>', texto)
    
    # Código `texto`
    texto = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', texto)
    
    # Remover emojis problemáticos
    texto = re.sub(r'[📋🔍✅⚠️❌]', '', texto)
    
    # Escapar caracteres especiais do HTML
    texto = texto.replace('&', '&amp;')
    texto = texto.replace('<', '&lt;').replace('>', '&gt;')
    texto = texto.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    texto = texto.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    texto = texto.replace('&lt;font name="Courier"&gt;', '<font name="Courier">')
    texto = texto.replace('&lt;/font&gt;', '</font>')
    
    return texto


if __name__ == '__main__':
    # Caminhos dos arquivos
    base_dir = Path(__file__).parent
    md_file = base_dir / 'ESTUDO_RASTREABILIDADE_BOVINA_FORMULARIOS.md'
    pdf_file = base_dir / 'ESTUDO_RASTREABILIDADE_BOVINA_FORMULARIOS.pdf'
    
    if not md_file.exists():
        print(f"❌ Arquivo Markdown não encontrado: {md_file}")
        exit(1)
    
    print(f"📄 Convertendo {md_file.name} para PDF...")
    processar_markdown_para_pdf(md_file, pdf_file)
    print(f"✅ Conversão concluída! PDF salvo em: {pdf_file}")




















