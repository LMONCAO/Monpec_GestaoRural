# -*- coding: utf-8 -*-
"""
Sistema de Relatórios em PDF para Todos os Módulos
Gera relatórios profissionais em PDF para tomada de decisão
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, 
    Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY

from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone


class GeradorRelatoriosPDF:
    """Classe base para gerar relatórios em PDF profissionais"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
    
    def _criar_estilos_customizados(self):
        """Cria estilos customizados para os relatórios"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2c5282'),
            spaceBefore=20,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        ))
        
        # Seção
        self.styles.add(ParagraphStyle(
            name='Secao',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#f7fafc'),
            borderPadding=8
        ))
        
        # Destaque
        self.styles.add(ParagraphStyle(
            name='Destaque',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        ))
        
        # Rodapé
        self.styles.add(ParagraphStyle(
            name='Rodape',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
            spaceBefore=20
        ))
    
    def _criar_cabecalho(self, elements, titulo: str, subtitulo: str = None):
        """Cria cabeçalho do relatório"""
        elements.append(Paragraph(titulo, self.styles['TituloPrincipal']))
        if subtitulo:
            elements.append(Paragraph(subtitulo, self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
    
    def _criar_rodape(self, elements):
        """Cria rodapé do relatório"""
        elements.append(Spacer(1, 0.5*inch))
        rodape_texto = f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Sistema MONPEC - Gestão Rural Inteligente"
        elements.append(Paragraph(rodape_texto, self.styles['Rodape']))
    
    def _criar_tabela_resumo(self, dados: List[List[str]], larguras_colunas: List[float] = None):
        """Cria tabela de resumo com estilo profissional"""
        if not larguras_colunas:
            larguras_colunas = [4*cm, 4*cm]
        
        tabela = Table(dados, colWidths=larguras_colunas)
        estilo = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # Corpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ])
        tabela.setStyle(estilo)
        return tabela
    
    def _criar_tabela_dados(self, dados: List[List[str]], larguras_colunas: List[float] = None):
        """Cria tabela de dados com estilo profissional"""
        if not larguras_colunas:
            num_cols = len(dados[0]) if dados else 1
            larguras_colunas = [4*cm] * num_cols
        
        tabela = Table(dados, colWidths=larguras_colunas)
        estilo = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
        tabela.setStyle(estilo)
        return tabela
    
    def _formatar_moeda(self, valor: Decimal) -> str:
        """Formata valor como moeda brasileira"""
        if valor is None:
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def _formatar_numero(self, valor: Any) -> str:
        """Formata número com separador de milhar"""
        if valor is None:
            return "0"
        return f"{valor:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def gerar_pdf(self, elements: List, filename: str) -> BytesIO:
        """Gera o PDF final"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        doc.build(elements)
        buffer.seek(0)
        return buffer


# ===== RELATÓRIO DE PECUÁRIA =====

def gerar_relatorio_pecuaria_pdf(propriedade) -> BytesIO:
    """Gera relatório completo de Pecuária em PDF"""
    from .models import (
        InventarioRebanho, MovimentacaoProjetada, AnimalIndividual,
        Touro, IATF, EstacaoMonta, ParametrosProjecaoRebanho
    )
    
    gerador = GeradorRelatoriosPDF()
    elements = []
    
    # Cabeçalho
    gerador._criar_cabecalho(
        elements,
        f"Relatório de Pecuária",
        f"{propriedade.nome_propriedade} - {propriedade.municipio}/{propriedade.uf}"
    )
    
    # 1. RESUMO EXECUTIVO
    elements.append(Paragraph("📊 Resumo Executivo", gerador.styles['Secao']))
    
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais = sum(item.quantidade for item in inventario)
    valor_total = sum(item.valor_total or Decimal('0') for item in inventario)
    
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Total de Animais', gerador._formatar_numero(total_animais)],
        ['Valor Total do Rebanho', gerador._formatar_moeda(valor_total)],
        ['Categorias Cadastradas', str(inventario.values('categoria').distinct().count())],
    ]
    
    # Adicionar dados de reprodução
    touros_aptos = Touro.objects.filter(propriedade=propriedade, apto=True).count()
    iatfs_pendentes = IATF.objects.filter(propriedade=propriedade, status='PENDENTE').count()
    
    resumo_data.append(['Touros Aptos', str(touros_aptos)])
    resumo_data.append(['IATFs Pendentes', str(iatfs_pendentes)])
    
    elements.append(gerador._criar_tabela_resumo(resumo_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 2. INVENTÁRIO POR CATEGORIA
    elements.append(Paragraph("🐄 Inventário por Categoria", gerador.styles['Secao']))
    
    inventario_por_cat = inventario.values('categoria__nome').annotate(
        total=Sum('quantidade'),
        valor=Sum('valor_total')
    ).order_by('categoria__nome')
    
    if inventario_por_cat:
        dados_tabela = [['Categoria', 'Quantidade', 'Valor Total']]
        for item in inventario_por_cat:
            dados_tabela.append([
                item['categoria__nome'],
                gerador._formatar_numero(item['total'] or 0),
                gerador._formatar_moeda(item['valor'] or Decimal('0'))
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [6*cm, 3*cm, 3*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. ANIMAIS RASTREADOS
    animais_rastreados = AnimalIndividual.objects.filter(propriedade=propriedade).count()
    if animais_rastreados > 0:
        elements.append(Paragraph("🏷️ Rastreabilidade", gerador.styles['Secao']))
        rastreabilidade_data = [
            ['Métrica', 'Valor'],
            ['Animais Rastreados', gerador._formatar_numero(animais_rastreados)],
        ]
        elements.append(gerador._criar_tabela_resumo(rastreabilidade_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # 4. REPRODUÇÃO
    elements.append(Paragraph("💚 Reprodução", gerador.styles['Secao']))
    
    reproducao_data = [
        ['Métrica', 'Valor'],
        ['Touros Cadastrados', str(Touro.objects.filter(propriedade=propriedade).count())],
        ['Touros Aptos', str(touros_aptos)],
        ['Estações de Monta', str(EstacaoMonta.objects.filter(propriedade=propriedade).count())],
        ['IATFs Realizadas', str(IATF.objects.filter(propriedade=propriedade).count())],
        ['IATFs Pendentes', str(iatfs_pendentes)],
    ]
    elements.append(gerador._criar_tabela_resumo(reproducao_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 5. PROJEÇÕES
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    if parametros:
        elements.append(Paragraph("📈 Parâmetros de Projeção", gerador.styles['Secao']))
        projecao_data = [
            ['Parâmetro', 'Valor'],
            ['Taxa de Natalidade', f"{parametros.taxa_natalidade or 0:.1f}%"],
            ['Taxa de Mortalidade (Bezerros)', f"{parametros.taxa_mortalidade_bezerros or 0:.1f}%"],
            ['Taxa de Mortalidade (Adultos)', f"{parametros.taxa_mortalidade_adultos or 0:.1f}%"],
        ]
        elements.append(gerador._criar_tabela_resumo(projecao_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # Rodapé
    gerador._criar_rodape(elements)
    
    return gerador.gerar_pdf(elements, f"relatorio_pecuaria_{propriedade.id}.pdf")


# ===== RELATÓRIO DE NUTRIÇÃO =====

def gerar_relatorio_nutricao_pdf(propriedade) -> BytesIO:
    """Gera relatório completo de Nutrição em PDF"""
    from .models_operacional import (
        EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao
    )
    from .models_controles_operacionais import Cocho, ControleCocho
    
    gerador = GeradorRelatoriosPDF()
    elements = []
    
    # Cabeçalho
    gerador._criar_cabecalho(
        elements,
        f"Relatório de Nutrição",
        f"{propriedade.nome_propriedade} - {propriedade.municipio}/{propriedade.uf}"
    )
    
    # 1. RESUMO EXECUTIVO
    elements.append(Paragraph("📊 Resumo Executivo", gerador.styles['Secao']))
    
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    valor_total_estoque = sum(estoque.valor_total_estoque or Decimal('0') for estoque in estoques)
    quantidade_total = sum(estoque.quantidade_atual or Decimal('0') for estoque in estoques)
    estoques_baixo = estoques.filter(quantidade_atual__lte=F('quantidade_minima')).count()
    
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Itens em Estoque', str(estoques.count())],
        ['Quantidade Total', gerador._formatar_numero(quantidade_total)],
        ['Valor Total do Estoque', gerador._formatar_moeda(valor_total_estoque)],
        ['Estoques Abaixo do Mínimo', str(estoques_baixo)],
    ]
    elements.append(gerador._criar_tabela_resumo(resumo_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 2. ESTOQUES
    elements.append(Paragraph("📦 Estoque de Suplementação", gerador.styles['Secao']))
    
    if estoques.exists():
        dados_tabela = [['Produto', 'Quantidade', 'Unidade', 'Valor Total', 'Status']]
        for estoque in estoques[:20]:  # Limitar a 20 itens
            status = "⚠️ Baixo" if estoque.quantidade_atual <= estoque.quantidade_minima else "✅ OK"
            dados_tabela.append([
                estoque.tipo_suplemento if hasattr(estoque, 'tipo_suplemento') else str(estoque),
                gerador._formatar_numero(estoque.quantidade_atual or 0),
                estoque.unidade_medida or 'kg',
                gerador._formatar_moeda(estoque.valor_total_estoque or Decimal('0')),
                status
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [4*cm, 2*cm, 2*cm, 2.5*cm, 2*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. COMPRAS DO MÊS
    mes_atual = timezone.now().replace(day=1)
    compras_mes = CompraSuplementacao.objects.filter(
        estoque__propriedade=propriedade,
        data__gte=mes_atual
    )
    
    if compras_mes.exists():
        elements.append(Paragraph("🛒 Compras do Mês", gerador.styles['Secao']))
        valor_compras = sum(compra.valor_total or Decimal('0') for compra in compras_mes)
        compras_data = [
            ['Métrica', 'Valor'],
            ['Compras Realizadas', str(compras_mes.count())],
            ['Valor Total', gerador._formatar_moeda(valor_compras)],
        ]
        elements.append(gerador._criar_tabela_resumo(compras_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # 4. DISTRIBUIÇÕES DO MÊS
    distribuicoes_mes = DistribuicaoSuplementacao.objects.filter(
        estoque__propriedade=propriedade,
        data__gte=mes_atual
    )
    
    if distribuicoes_mes.exists():
        elements.append(Paragraph("🚚 Distribuições do Mês", gerador.styles['Secao']))
        quantidade_distribuida = sum(dist.quantidade or Decimal('0') for dist in distribuicoes_mes)
        distribuicoes_data = [
            ['Métrica', 'Valor'],
            ['Distribuições Realizadas', str(distribuicoes_mes.count())],
            ['Quantidade Distribuída', gerador._formatar_numero(quantidade_distribuida)],
        ]
        elements.append(gerador._criar_tabela_resumo(distribuicoes_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # 5. COCHOS
    cochos = Cocho.objects.filter(propriedade=propriedade)
    if cochos.exists():
        elements.append(Paragraph("🪣 Cochos", gerador.styles['Secao']))
        cochos_ativos = cochos.filter(ativo=True).count()
        cochos_data = [
            ['Métrica', 'Valor'],
            ['Total de Cochos', str(cochos.count())],
            ['Cochos Ativos', str(cochos_ativos)],
        ]
        elements.append(gerador._criar_tabela_resumo(cochos_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # Rodapé
    gerador._criar_rodape(elements)
    
    return gerador.gerar_pdf(elements, f"relatorio_nutricao_{propriedade.id}.pdf")


# ===== RELATÓRIO DE OPERAÇÕES =====

def gerar_relatorio_operacoes_pdf(propriedade) -> BytesIO:
    """Gera relatório completo de Operações em PDF"""
    from .models_operacional import (
        TanqueCombustivel, ConsumoCombustivel, Equipamento, ManutencaoEquipamento
    )
    from .models_funcionarios import Funcionario, FolhaPagamento
    
    gerador = GeradorRelatoriosPDF()
    elements = []
    
    # Cabeçalho
    gerador._criar_cabecalho(
        elements,
        f"Relatório de Operações",
        f"{propriedade.nome_propriedade} - {propriedade.municipio}/{propriedade.uf}"
    )
    
    # 1. RESUMO EXECUTIVO
    elements.append(Paragraph("📊 Resumo Executivo", gerador.styles['Secao']))
    
    equipamentos = Equipamento.objects.filter(propriedade=propriedade)
    equipamentos_ativos = equipamentos.filter(ativo=True).count()
    manutencoes_pendentes = ManutencaoEquipamento.objects.filter(
        equipamento__propriedade=propriedade,
        status='PENDENTE'
    ).count()
    
    funcionarios = Funcionario.objects.filter(propriedade=propriedade)
    funcionarios_ativos = funcionarios.filter(ativo=True).count()
    
    mes_atual = timezone.now().replace(day=1)
    folha_mes = FolhaPagamento.objects.filter(
        propriedade=propriedade,
        mes_referencia__gte=mes_atual
    ).first()
    valor_folha = folha_mes.valor_total if folha_mes else Decimal('0')
    
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Equipamentos Cadastrados', str(equipamentos.count())],
        ['Equipamentos Ativos', str(equipamentos_ativos)],
        ['Manutenções Pendentes', str(manutencoes_pendentes)],
        ['Funcionários Cadastrados', str(funcionarios.count())],
        ['Funcionários Ativos', str(funcionarios_ativos)],
        ['Folha de Pagamento (Mês)', gerador._formatar_moeda(valor_folha)],
    ]
    elements.append(gerador._criar_tabela_resumo(resumo_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 2. COMBUSTÍVEL
    tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
    if tanques.exists():
        elements.append(Paragraph("⛽ Combustível", gerador.styles['Secao']))
        
        estoque_total = sum(tanque.estoque_atual or Decimal('0') for tanque in tanques)
        consumo_mes = ConsumoCombustivel.objects.filter(
            tanque__propriedade=propriedade,
            data__gte=mes_atual
        ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')
        
        combustivel_data = [
            ['Métrica', 'Valor'],
            ['Tanques Cadastrados', str(tanques.count())],
            ['Estoque Total', f"{estoque_total:.2f} L"],
            ['Consumo do Mês', f"{consumo_mes:.2f} L"],
        ]
        elements.append(gerador._criar_tabela_resumo(combustivel_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. EQUIPAMENTOS
    if equipamentos.exists():
        elements.append(Paragraph("🔧 Equipamentos", gerador.styles['Secao']))
        dados_tabela = [['Equipamento', 'Tipo', 'Status', 'Manutenções Pendentes']]
        for equip in equipamentos[:15]:  # Limitar a 15
            manut_pend = ManutencaoEquipamento.objects.filter(
                equipamento=equip,
                status='PENDENTE'
            ).count()
            status = "✅ Ativo" if equip.ativo else "❌ Inativo"
            dados_tabela.append([
                equip.descricao or str(equip),
                equip.tipo or '-',
                status,
                str(manut_pend)
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [5*cm, 3*cm, 2*cm, 3*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 4. FUNCIONÁRIOS
    if funcionarios.exists():
        elements.append(Paragraph("👥 Funcionários", gerador.styles['Secao']))
        dados_tabela = [['Nome', 'Cargo', 'Status', 'Salário']]
        for func in funcionarios[:15]:  # Limitar a 15
            status = "✅ Ativo" if func.ativo else "❌ Inativo"
            salario = gerador._formatar_moeda(func.salario_base or Decimal('0'))
            dados_tabela.append([
                func.nome_completo or str(func),
                func.cargo or '-',
                status,
                salario
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [5*cm, 3*cm, 2*cm, 3*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # Rodapé
    gerador._criar_rodape(elements)
    
    return gerador.gerar_pdf(elements, f"relatorio_operacoes_{propriedade.id}.pdf")


# ===== RELATÓRIO DE COMPRAS =====

def gerar_relatorio_compras_pdf(propriedade) -> BytesIO:
    """Gera relatório completo de Compras em PDF"""
    from .models_compras_financeiro import (
        RequisicaoCompra, OrdemCompra, Fornecedor, SetorCompra
    )
    
    gerador = GeradorRelatoriosPDF()
    elements = []
    
    # Cabeçalho
    gerador._criar_cabecalho(
        elements,
        f"Relatório de Compras",
        f"{propriedade.nome_propriedade} - {propriedade.municipio}/{propriedade.uf}"
    )
    
    # 1. RESUMO EXECUTIVO
    elements.append(Paragraph("📊 Resumo Executivo", gerador.styles['Secao']))
    
    requisicoes = RequisicaoCompra.objects.filter(propriedade=propriedade)
    # Status pendentes: não concluídas, não canceladas
    requisicoes_pendentes = requisicoes.exclude(
        status__in=['CONCLUIDA', 'CANCELADA']
    ).count()
    
    ordens = OrdemCompra.objects.filter(propriedade=propriedade)
    # Status pendentes: não concluídas, não canceladas
    ordens_pendentes = ordens.exclude(
        status__in=['CONCLUIDA', 'CANCELADA', 'RECEBIDA']
    ).count()
    ordens_pend = ordens.exclude(status__in=['CONCLUIDA', 'CANCELADA', 'RECEBIDA'])
    valor_ordens_pendentes = sum(getattr(ordem, 'valor_total', None) or Decimal('0') for ordem in ordens_pend)
    
    fornecedores = Fornecedor.objects.filter(propriedade=propriedade)
    
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Requisições Cadastradas', str(requisicoes.count())],
        ['Requisições Pendentes', str(requisicoes_pendentes)],
        ['Ordens de Compra', str(ordens.count())],
        ['Ordens Pendentes', str(ordens_pendentes)],
        ['Valor Ordens Pendentes', gerador._formatar_moeda(valor_ordens_pendentes)],
        ['Fornecedores Cadastrados', str(fornecedores.count())],
    ]
    elements.append(gerador._criar_tabela_resumo(resumo_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 2. REQUISIÇÕES PENDENTES
    if requisicoes_pendentes > 0:
        elements.append(Paragraph("📋 Requisições Pendentes", gerador.styles['Secao']))
        req_pendentes = requisicoes.exclude(status__in=['CONCLUIDA', 'CANCELADA'])[:10]
        dados_tabela = [['Requisição', 'Setor', 'Data', 'Valor Estimado']]
        for req in req_pendentes:
            # Usar método valor_estimado_total se disponível, senão calcular
            valor_est = getattr(req, 'valor_estimado_total', None)
            if valor_est is None and hasattr(req, 'itens'):
                valor_est = sum(item.valor_estimado_total for item in req.itens.all())
            dados_tabela.append([
                getattr(req, 'titulo', None) or f"Requisição #{req.id}",
                req.setor.nome if hasattr(req, 'setor') and req.setor else '-',
                req.data_criacao.strftime('%d/%m/%Y') if hasattr(req, 'data_criacao') else '-',
                gerador._formatar_moeda(valor_est or Decimal('0'))
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [4*cm, 3*cm, 2.5*cm, 3*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. ORDENS PENDENTES
    if ordens_pendentes > 0:
        elements.append(Paragraph("🛒 Ordens de Compra Pendentes", gerador.styles['Secao']))
        ord_pendentes = ordens.exclude(status__in=['CONCLUIDA', 'CANCELADA', 'RECEBIDA'])[:10]
        dados_tabela = [['Ordem', 'Fornecedor', 'Data', 'Valor Total']]
        for ordem in ord_pendentes:
            dados_tabela.append([
                getattr(ordem, 'numero_ordem', None) or getattr(ordem, 'numero', None) or f"#{ordem.id}",
                ordem.fornecedor.nome if hasattr(ordem, 'fornecedor') and ordem.fornecedor else '-',
                ordem.data_emissao.strftime('%d/%m/%Y') if hasattr(ordem, 'data_emissao') else '-',
                gerador._formatar_moeda(getattr(ordem, 'valor_total', None) or Decimal('0'))
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [3*cm, 4*cm, 2.5*cm, 3*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 4. FORNECEDORES
    if fornecedores.exists():
        elements.append(Paragraph("🏢 Fornecedores", gerador.styles['Secao']))
        dados_tabela = [['Nome', 'CNPJ/CPF', 'Contato']]
        for forn in fornecedores[:15]:  # Limitar a 15
            dados_tabela.append([
                forn.nome or str(forn),
                forn.cnpj_cpf or '-',
                forn.telefone or forn.email or '-'
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [5*cm, 4*cm, 4*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # Rodapé
    gerador._criar_rodape(elements)
    
    return gerador.gerar_pdf(elements, f"relatorio_compras_{propriedade.id}.pdf")


# ===== RELATÓRIO DE PROJETOS BANCÁRIOS =====

def gerar_relatorio_projetos_bancarios_pdf(propriedade) -> BytesIO:
    """Gera relatório completo de Projetos Bancários em PDF"""
    from .models import ProjetoBancario, DocumentoProjeto
    
    gerador = GeradorRelatoriosPDF()
    elements = []
    
    # Cabeçalho
    gerador._criar_cabecalho(
        elements,
        f"Relatório de Projetos Bancários",
        f"{propriedade.nome_propriedade} - {propriedade.municipio}/{propriedade.uf}"
    )
    
    # 1. RESUMO EXECUTIVO
    elements.append(Paragraph("📊 Resumo Executivo", gerador.styles['Secao']))
    
    projetos = ProjetoBancario.objects.filter(propriedade=propriedade)
    projetos_aprovados = projetos.filter(status='APROVADO').count()
    projetos_pendentes = projetos.filter(status='ANALISE').count()
    valor_total_projetos = sum(proj.valor_solicitado or Decimal('0') for proj in projetos)
    
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Total de Projetos', str(projetos.count())],
        ['Projetos Aprovados', str(projetos_aprovados)],
        ['Projetos em Análise', str(projetos_pendentes)],
        ['Valor Total Solicitado', gerador._formatar_moeda(valor_total_projetos)],
    ]
    elements.append(gerador._criar_tabela_resumo(resumo_data))
    elements.append(Spacer(1, 0.3*inch))
    
    # 2. PROJETOS
    if projetos.exists():
        elements.append(Paragraph("📄 Projetos", gerador.styles['Secao']))
        dados_tabela = [['Projeto', 'Tipo', 'Status', 'Valor Solicitado', 'Data']]
        for proj in projetos:
            status_display = dict(ProjetoBancario.STATUS_CHOICES).get(proj.status, proj.status)
            dados_tabela.append([
                proj.titulo or f"Projeto #{proj.id}",
                proj.tipo or '-',
                status_display,
                gerador._formatar_moeda(proj.valor_solicitado or Decimal('0')),
                proj.data_criacao.strftime('%d/%m/%Y') if hasattr(proj, 'data_criacao') else '-'
            ])
        elements.append(gerador._criar_tabela_dados(dados_tabela, [4*cm, 2.5*cm, 2.5*cm, 3*cm, 2.5*cm]))
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. DOCUMENTOS
    documentos = DocumentoProjeto.objects.filter(projeto__propriedade=propriedade)
    if documentos.exists():
        elements.append(Paragraph("📎 Documentos", gerador.styles['Secao']))
        docs_por_tipo = documentos.values('tipo').annotate(total=Count('id'))
        docs_data = [['Tipo de Documento', 'Quantidade']]
        for item in docs_por_tipo:
            docs_data.append([
                item['tipo'] or 'Outros',
                str(item['total'])
            ])
        elements.append(gerador._criar_tabela_resumo(docs_data))
        elements.append(Spacer(1, 0.3*inch))
    
    # Rodapé
    gerador._criar_rodape(elements)
    
    return gerador.gerar_pdf(elements, f"relatorio_projetos_bancarios_{propriedade.id}.pdf")

