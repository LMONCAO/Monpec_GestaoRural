# -*- coding: utf-8 -*-
"""
Script para gerar PDF de teste BND SISBOV
Cria um PDF com estrutura similar aos exportados do Portal SISBOV para testes
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date, timedelta
import random

def gerar_codigo_sisbov():
    """Gera um código SISBOV válido (BR + 13 dígitos)"""
    # Formato: BR + 13 dígitos
    # Exemplo: BR1234567890123
    numero = ''.join([str(random.randint(0, 9)) for _ in range(13)])
    return f"BR{numero}"

def gerar_numero_brinco():
    """Gera um número de brinco (15 dígitos)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(15)])

def gerar_numero_manejo(codigo_sisbov):
    """Extrai número de manejo do código SISBOV (posições 8-13)"""
    # Número de manejo são os últimos 6 dígitos do código SISBOV
    return codigo_sisbov[-6:]

def gerar_animais_teste(quantidade=10):
    """Gera lista de animais de teste"""
    racas = ['Nelore', 'Angus', 'Brahman', 'Brangus', 'Hereford', 'Simmental', 'Gir', 'Holandês']
    sexos = ['M', 'F']
    
    animais = []
    for i in range(quantidade):
        codigo_sisbov = gerar_codigo_sisbov()
        numero_manejo = gerar_numero_manejo(codigo_sisbov)
        numero_brinco = gerar_numero_brinco()
        raca = random.choice(racas)
        sexo = random.choice(sexos)
        
        # Data de nascimento aleatória nos últimos 3 anos
        data_nascimento = date.today() - timedelta(days=random.randint(100, 1000))
        
        # Peso aleatório entre 200 e 600 kg
        peso = random.randint(200, 600)
        
        animais.append({
            'codigo_sisbov': codigo_sisbov,
            'numero_manejo': numero_manejo,
            'numero_brinco': numero_brinco,
            'raca': raca,
            'sexo': 'Macho' if sexo == 'M' else 'Fêmea',
            'data_nascimento': data_nascimento.strftime('%d/%m/%Y'),
            'peso': peso
        })
    
    return animais

def criar_pdf_teste_bnd_sisbov(nome_arquivo='teste_bnd_sisbov.pdf', quantidade_animais=10):
    """Cria um PDF de teste com estrutura similar ao BND SISBOV"""
    
    # Gerar animais de teste
    animais = gerar_animais_teste(quantidade_animais)
    
    # Criar documento PDF
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Criar estilos customizados
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#3949ab'),
        alignment=TA_LEFT,
        spaceAfter=20
    )
    
    # Cabeçalho
    story.append(Paragraph('BASE NACIONAL DE DADOS - SISBOV', titulo_style))
    story.append(Paragraph('Sistema Brasileiro de Identificação e Certificação de Origem Bovina e Bubalina', 
                          styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Informações da Propriedade
    story.append(Paragraph('DADOS DO ESTABELECIMENTO RURAL', subtitulo_style))
    
    dados_propriedade = [
        ['Propriedade:', 'Fazenda Teste SISBOV'],
        ['CNPJ/CPF:', '12.345.678/0001-90'],
        ['Inscrição Estadual:', '123.456.789.012'],
        ['Data de Emissão:', date.today().strftime('%d/%m/%Y')],
    ]
    
    tabela_propriedade = Table(dados_propriedade, colWidths=[4*cm, 10*cm])
    tabela_propriedade.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tabela_propriedade)
    story.append(Spacer(1, 0.5*cm))
    
    # Tabela de Animais
    story.append(Paragraph('INVENTÁRIO DE ANIMAIS', subtitulo_style))
    
    # Cabeçalho da tabela
    dados_tabela = [[
        'Código SISBOV',
        'Nº Manejo',
        'Nº Brinco',
        'Raça',
        'Sexo',
        'Data Nasc.',
        'Peso (kg)'
    ]]
    
    # Adicionar animais
    for animal in animais:
        dados_tabela.append([
            animal['codigo_sisbov'],
            animal['numero_manejo'],
            animal['numero_brinco'],
            animal['raca'],
            animal['sexo'],
            animal['data_nascimento'],
            str(animal['peso'])
        ])
    
    # Criar tabela
    tabela_animais = Table(dados_tabela, colWidths=[3*cm, 1.5*cm, 3*cm, 2.5*cm, 1.5*cm, 2*cm, 1.5*cm])
    tabela_animais.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Linhas alternadas
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    story.append(tabela_animais)
    story.append(Spacer(1, 0.5*cm))
    
    # Resumo
    story.append(Paragraph(f'<b>Total de Animais:</b> {len(animais)}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f'Documento gerado em {date.today().strftime("%d/%m/%Y")} - Sistema de Teste BND SISBOV',
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(story)
    print(f"[OK] PDF de teste criado com sucesso: {nome_arquivo}")
    print(f"   Total de animais: {len(animais)}")
    print(f"\nAnimais gerados:")
    for i, animal in enumerate(animais[:5], 1):  # Mostrar apenas os 5 primeiros
        print(f"   {i}. {animal['codigo_sisbov']} - {animal['raca']} - {animal['sexo']}")
    if len(animais) > 5:
        print(f"   ... e mais {len(animais) - 5} animais")
    
    return nome_arquivo

if __name__ == '__main__':
    import sys
    
    quantidade = 10
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
        except ValueError:
            print("[AVISO] Quantidade invalida. Usando padrao: 10 animais")
    
    nome_arquivo = criar_pdf_teste_bnd_sisbov(quantidade_animais=quantidade)
    print(f"\n[ARQUIVO] Arquivo gerado: {nome_arquivo}")
    print("\n[DICA] Use este arquivo para testar a importacao BND SISBOV no sistema!")


