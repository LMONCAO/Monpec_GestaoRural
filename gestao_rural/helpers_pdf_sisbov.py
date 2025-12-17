# -*- coding: utf-8 -*-
"""
Helper para geração de PDFs SISBOV em conformidade com IN 17/2006
Padroniza cabeçalhos, rodapés e formatação dos anexos oficiais
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import date
from django.http import HttpResponse
from .models import Propriedade


class GeradorPDFSISBOV:
    """Classe helper para gerar PDFs SISBOV padronizados conforme IN 17/2006"""
    
    def __init__(self, propriedade: Propriedade, titulo_anexo: str, numero_anexo: str):
        """
        Inicializa o gerador de PDF SISBOV
        
        Args:
            propriedade: Objeto Propriedade
            titulo_anexo: Título do anexo (ex: "FORMULÁRIO PARA INVENTÁRIO DE ANIMAIS")
            numero_anexo: Número do anexo (ex: "VI")
        """
        self.propriedade = propriedade
        self.titulo_anexo = titulo_anexo
        self.numero_anexo = numero_anexo
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
    
    def _criar_estilos_customizados(self):
        """Cria estilos customizados para documentos SISBOV"""
        
        # Estilo para título principal do anexo
        self.styles.add(ParagraphStyle(
            'TituloAnexo',
            parent=self.styles['Heading1'],
            fontSize=14,
            leading=18,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a237e'),  # Azul escuro oficial
        ))
        
        # Estilo para subtítulo (IN 17/2006)
        self.styles.add(ParagraphStyle(
            'SubtituloNormativo',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.HexColor('#424242'),
            fontStyle='italic',
        ))
        
        # Estilo para cabeçalho de seção
        self.styles.add(ParagraphStyle(
            'CabecalhoSecao',
            parent=self.styles['Heading2'],
            fontSize=11,
            leading=14,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a237e'),
        ))
        
        # Estilo para informações da propriedade
        self.styles.add(ParagraphStyle(
            'InfoPropriedade',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=4,
            fontName='Helvetica',
        ))
        
        # Estilo para rodapé oficial
        self.styles.add(ParagraphStyle(
            'RodapeOficial',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.HexColor('#616161'),
            fontStyle='italic',
        ))
        
        # Estilo para campo de assinatura
        self.styles.add(ParagraphStyle(
            'CampoAssinatura',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.black,
        ))
    
    def criar_cabecalho_oficial(self, story):
        """
        Cria cabeçalho oficial conforme padrão SISBOV
        
        Args:
            story: Lista de elementos do PDF
        """
        # Linha superior com brasão/logotipo (se disponível)
        # Por enquanto, apenas texto
        
        # Título do anexo
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            f'ANEXO {self.numero_anexo} - {self.titulo_anexo}',
            self.styles['TituloAnexo']
        ))
        
        # Subtítulo normativo
        story.append(Paragraph(
            'Conforme Instrução Normativa MAPA nº 17, de 13 de julho de 2006',
            self.styles['SubtituloNormativo']
        ))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Linha divisória
        story.append(Paragraph(
            '─' * 80,
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3*cm))
    
    def criar_dados_propriedade(self, story, incluir_produtor=True):
        """
        Cria seção com dados da propriedade
        
        Args:
            story: Lista de elementos do PDF
            incluir_produtor: Se True, inclui dados do produtor rural
        """
        story.append(Paragraph('<b>DADOS DO ESTABELECIMENTO RURAL</b>', self.styles['CabecalhoSecao']))
        
        dados_propriedade = [
            ['Nome do Estabelecimento:', self.propriedade.nome_propriedade or '—'],
            ['Município/UF:', f'{self.propriedade.municipio or "—"} / {self.propriedade.uf or "—"}'],
            ['Endereço:', self.propriedade.endereco or '—'],
            ['CEP:', self.propriedade.cep or '—'],
        ]
        
        if self.propriedade.nirf:
            dados_propriedade.append(['NIRF:', self.propriedade.nirf])
        if self.propriedade.car:
            dados_propriedade.append(['CAR:', self.propriedade.car])
        
        dados_propriedade.append(['Data de Emissão:', date.today().strftime('%d/%m/%Y')])
        
        if incluir_produtor and hasattr(self.propriedade, 'produtor_rural') and self.propriedade.produtor_rural:
            produtor = self.propriedade.produtor_rural
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph('<b>DADOS DO PRODUTOR RURAL</b>', self.styles['CabecalhoSecao']))
            dados_propriedade.extend([
                ['Nome:', produtor.nome or '—'],
                ['CPF/CNPJ:', produtor.cpf_cnpj or '—'],
                ['RG:', produtor.rg or '—'],
            ])
        
        tabela_propriedade = Table(dados_propriedade, colWidths=[5*cm, 11*cm])
        tabela_propriedade.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdbdbd')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ]))
        
        story.append(tabela_propriedade)
        story.append(Spacer(1, 0.4*cm))
    
    def criar_tabela_dados(self, story, dados, colunas, larguras=None, titulo=None):
        """
        Cria tabela padronizada com dados
        
        Args:
            story: Lista de elementos do PDF
            dados: Lista de listas com os dados da tabela
            colunas: Lista com nomes das colunas
            larguras: Lista com larguras das colunas (opcional)
            titulo: Título da tabela (opcional)
        """
        if titulo:
            story.append(Paragraph(f'<b>{titulo}</b>', self.styles['CabecalhoSecao']))
        
        # Adicionar cabeçalho
        dados_tabela = [colunas] + dados
        
        if not larguras:
            # Calcular larguras automaticamente
            largura_total = 16*cm
            num_cols = len(colunas)
            larguras = [largura_total / num_cols] * num_cols
        
        tabela = Table(dados_tabela, colWidths=larguras)
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Azul escuro oficial
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#757575')),
            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(tabela)
        story.append(Spacer(1, 0.3*cm))
    
    def criar_campo_assinatura(self, story, nome_campo="Responsável Técnico"):
        """
        Cria campo para assinatura
        
        Args:
            story: Lista de elementos do PDF
            nome_campo: Nome do campo de assinatura
        """
        story.append(Spacer(1, 1*cm))
        
        # Linha para assinatura
        dados_assinatura = [
            ['', ''],
            [f'{nome_campo}:', ''],
            ['', ''],
        ]
        
        tabela_assinatura = Table(dados_assinatura, colWidths=[5*cm, 11*cm])
        tabela_assinatura.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(tabela_assinatura)
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            f'<i>Nome e assinatura do {nome_campo.lower()}</i>',
            self.styles['RodapeOficial']
        ))
    
    def criar_rodape_oficial(self, story, numero_pagina=True):
        """
        Cria rodapé oficial conforme padrão SISBOV
        
        Args:
            story: Lista de elementos do PDF
            numero_pagina: Se True, inclui numeração de páginas
        """
        story.append(Spacer(1, 0.5*cm))
        
        # Linha divisória
        story.append(Paragraph('─' * 80, self.styles['Normal']))
        story.append(Spacer(1, 0.2*cm))
        
        # Texto do rodapé
        rodape_texto = (
            f'Documento gerado em {date.today().strftime("%d/%m/%Y")} | '
            f'Conforme Instrução Normativa MAPA nº 17/2006 | '
            f'Sistema MONPEC - Gestão Rural'
        )
        
        story.append(Paragraph(rodape_texto, self.styles['RodapeOficial']))
        
        if numero_pagina:
            # A numeração será adicionada pelo SimpleDocTemplate
            pass
    
    def criar_declaracao_veracidade(self, story):
        """
        Cria declaração de veracidade das informações
        
        Args:
            story: Lista de elementos do PDF
        """
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            '<b>DECLARAÇÃO DE VERACIDADE</b>',
            self.styles['CabecalhoSecao']
        ))
        
        declaracao = (
            'Declaro, sob as penas da lei, que as informações constantes neste documento '
            'são verdadeiras e corretas, assumindo total responsabilidade pela veracidade '
            'dos dados declarados e pela conformidade com a Instrução Normativa MAPA nº 17/2006.'
        )
        
        story.append(Paragraph(declaracao, self.styles['InfoPropriedade']))
        story.append(Spacer(1, 0.3*cm))
    
    def criar_documento_pdf(self, filename_base: str, story, margens_padrao=True):
        """
        Cria o documento PDF final
        
        Args:
            filename_base: Nome base do arquivo (sem extensão)
            story: Lista de elementos do PDF
            margens_padrao: Se True, usa margens padrão SISBOV
        
        Returns:
            HttpResponse com o PDF
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="SISBOV_Anexo_{self.numero_anexo}_{filename_base}_'
            f'{self.propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
        )
        
        if margens_padrao:
            # Margens padrão para documentos oficiais SISBOV
            top_margin = 2.5*cm
            bottom_margin = 2*cm
            left_margin = 2*cm
            right_margin = 2*cm
        else:
            top_margin = 2*cm
            bottom_margin = 2*cm
            left_margin = 2*cm
            right_margin = 2*cm
        
        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=right_margin,
            leftMargin=left_margin,
            topMargin=top_margin,
            bottomMargin=bottom_margin
        )
        
        # Adicionar numeração de páginas
        def adicionar_numero_pagina(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            text = f'Página {page_num}'
            canvas.drawRightString(A4[0] - right_margin, bottom_margin - 0.5*cm, text)
            canvas.restoreState()
        
        doc.build(story, onFirstPage=adicionar_numero_pagina, onLaterPages=adicionar_numero_pagina)
        
        return response







