# -*- coding: utf-8 -*-
"""
Views para Relatórios Oficiais SISBOV - Anexos Obrigatórios
Conforme Instrução Normativa MAPA nº 17/2006
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q, Count, Sum
from django.db import connection
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

try:
    from .helpers_pdf_sisbov import GeradorPDFSISBOV
except ImportError:
    GeradorPDFSISBOV = None


@login_required
def relatorios_sisbov_menu(request, propriedade_id):
    """Menu principal de relatórios SISBOV"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Lista de anexos disponíveis (IN 17/2006)
    anexos = [
        {
            'numero': 'IV',
            'nome': 'Cadastro de Produtor Rural',
            'descricao': 'Cadastro de produtor rural no SISBOV',
            'url': 'relatorio_sisbov_anexo_iv',
            'url_pdf': 'relatorio_sisbov_anexo_iv_pdf',
            'obrigatorio': True,
            'prioridade': 'baixa',
        },
        {
            'numero': 'V',
            'nome': 'Cadastro de Estabelecimento Rural',
            'descricao': 'Cadastro de estabelecimento rural no SISBOV',
            'url': 'relatorio_sisbov_anexo_v',
            'url_pdf': 'relatorio_sisbov_anexo_v_pdf',
            'obrigatorio': True,
            'prioridade': 'baixa',
        },
        {
            'numero': 'VI',
            'nome': 'Inventário de Animais',
            'descricao': 'Formulário para inventário de animais conforme SISBOV',
            'url': 'relatorio_sisbov_anexo_vi',
            'url_pdf': 'relatorio_sisbov_anexo_vi_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'VII',
            'nome': 'Termo de Adesão',
            'descricao': 'Termo de adesão à norma operacional do SISBOV',
            'url': 'relatorio_sisbov_anexo_vii',
            'url_pdf': 'relatorio_sisbov_anexo_vii_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'VIII',
            'nome': 'Protocolo Declaratório de Produção',
            'descricao': 'Protocolo declaratório de produção',
            'url': 'relatorio_sisbov_anexo_viii',
            'url_pdf': 'relatorio_sisbov_anexo_viii_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'IX',
            'nome': 'Comunicado de Entrada de Animais',
            'descricao': 'Comunicado de entrada de animais na propriedade',
            'url': 'relatorio_sisbov_anexo_ix',
            'url_pdf': 'relatorio_sisbov_anexo_ix_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'X',
            'nome': 'Comunicado de Saída de Animais',
            'descricao': 'Comunicado de saída de animais da propriedade',
            'url': 'relatorio_sisbov_anexo_x',
            'url_pdf': 'relatorio_sisbov_anexo_x_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'XI',
            'nome': 'Declaração de Nascimento',
            'descricao': 'Declaração de nascimento de animais',
            'url': 'relatorio_sisbov_anexo_xi',
            'url_pdf': 'relatorio_sisbov_anexo_xi_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'XII',
            'nome': 'Declaração de Morte',
            'descricao': 'Declaração de morte de animais',
            'url': 'relatorio_sisbov_anexo_xii',
            'url_pdf': 'relatorio_sisbov_anexo_xii_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
        {
            'numero': 'XIII',
            'nome': 'Declaração de Perda de Brinco',
            'descricao': 'Declaração de perda de brinco de identificação',
            'url': 'relatorio_sisbov_anexo_xiii',
            'url_pdf': 'relatorio_sisbov_anexo_xiii_pdf',
            'obrigatorio': True,
            'prioridade': 'media',
        },
        {
            'numero': 'XIV',
            'nome': 'Declaração de Mudança de Categoria',
            'descricao': 'Declaração de mudança de categoria do animal',
            'url': 'relatorio_sisbov_anexo_xiv',
            'url_pdf': 'relatorio_sisbov_anexo_xiv_pdf',
            'obrigatorio': True,
            'prioridade': 'media',
        },
        {
            'numero': 'XV',
            'nome': 'Declaração de Mudança de Propriedade',
            'descricao': 'Declaração de mudança de propriedade do animal',
            'url': 'relatorio_sisbov_anexo_xv',
            'url_pdf': 'relatorio_sisbov_anexo_xv_pdf',
            'obrigatorio': True,
            'prioridade': 'media',
        },
        {
            'numero': 'XVI',
            'nome': 'Declaração de Abate',
            'descricao': 'Declaração de abate de animais',
            'url': 'relatorio_sisbov_anexo_xvi',
            'url_pdf': 'relatorio_sisbov_anexo_xvi_pdf',
            'obrigatorio': True,
            'prioridade': 'baixa',
        },
        {
            'numero': 'XVII',
            'nome': 'Declaração de Exportação',
            'descricao': 'Declaração de exportação de animais',
            'url': 'relatorio_sisbov_anexo_xvii',
            'url_pdf': 'relatorio_sisbov_anexo_xvii_pdf',
            'obrigatorio': True,
            'prioridade': 'baixa',
        },
        {
            'numero': 'XVIII',
            'nome': 'Declaração de Importação',
            'descricao': 'Declaração de importação de animais',
            'url': 'relatorio_sisbov_anexo_xviii',
            'url_pdf': 'relatorio_sisbov_anexo_xviii_pdf',
            'obrigatorio': True,
            'prioridade': 'baixa',
        },
        {
            'numero': 'XIX',
            'nome': 'Declaração de Movimentação',
            'descricao': 'Declaração de movimentação de animais',
            'url': 'relatorio_sisbov_anexo_xix',
            'url_pdf': 'relatorio_sisbov_anexo_xix_pdf',
            'obrigatorio': True,
            'prioridade': 'alta',
        },
    ]
    
    context = {
        'propriedade': propriedade,
        'anexos': anexos,
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov_menu.html', context)


def _campo_existe_no_banco(tabela, campo):
    """Verifica se um campo existe em uma tabela do banco de dados PostgreSQL"""
    try:
        with connection.cursor() as cursor:
            # Sistema usa apenas PostgreSQL
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, [tabela, campo])
            return cursor.fetchone() is not None
    except Exception:
        return False


@login_required
def relatorio_sisbov_anexo_vi(request, propriedade_id):
    """
    Anexo VI - Formulário para Inventário de Animais
    Lista todos os animais da propriedade com seus dados de identificação
    """
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar todos os animais ativos
    # Usar only() para especificar apenas os campos necessários, evitando campos que podem não existir
    # Isso evita o erro quando o campo cota_hilton não existe no banco de dados
    campos_necessarios = [
        'id', 'codigo_sisbov', 'numero_manejo', 'numero_brinco', 
        'categoria_id', 'raca', 'sexo', 'data_nascimento', 'status',
        'propriedade_id', 'propriedade_origem_id'
    ]
    
    animais = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).select_related('categoria', 'propriedade_origem').only(*campos_necessarios).order_by('codigo_sisbov', 'numero_brinco')
    
    # Estatísticas
    total_animais = animais.count()
    animais_por_categoria = animais.values('categoria__nome').annotate(
        total=Count('id')
    ).order_by('categoria__nome')
    
    context = {
        'propriedade': propriedade,
        'animais': animais,
        'total_animais': total_animais,
        'animais_por_categoria': animais_por_categoria,
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_vi_inventario.html', context)


@login_required
def relatorio_sisbov_anexo_vi_pdf(request, propriedade_id):
    """Gera PDF do Anexo VI - Inventário de Animais (Conforme IN 17/2006)"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar animais ativos
    # Usar only() para especificar apenas os campos necessários, evitando campos que podem não existir
    # Isso evita o erro quando o campo cota_hilton não existe no banco de dados
    campos_necessarios = [
        'id', 'codigo_sisbov', 'numero_manejo', 'numero_brinco', 
        'categoria_id', 'raca', 'sexo', 'data_nascimento', 'status',
        'propriedade_id', 'propriedade_origem_id'
    ]
    
    animais = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).select_related('categoria').only(*campos_necessarios).order_by('codigo_sisbov', 'numero_brinco')
    
    # Usar helper padronizado se disponível
    if GeradorPDFSISBOV:
        gerador = GeradorPDFSISBOV(
            propriedade=propriedade,
            titulo_anexo="FORMULÁRIO PARA INVENTÁRIO DE ANIMAIS",
            numero_anexo="VI"
        )
        
        story = []
        
        # Cabeçalho oficial
        gerador.criar_cabecalho_oficial(story)
        
        # Dados da propriedade
        gerador.criar_dados_propriedade(story, incluir_produtor=True)
        
        # Preparar dados da tabela
        dados_animais = []
        for animal in animais:
            dados_animais.append([
                animal.codigo_sisbov or '—',
                animal.numero_manejo or '—',
                animal.numero_brinco or '—',
                animal.categoria.nome if animal.categoria else '—',
                animal.raca or '—',
                'Fêmea' if animal.sexo == 'F' else 'Macho',
                animal.data_nascimento.strftime('%d/%m/%Y') if animal.data_nascimento else '—',
                animal.get_status_display(),
            ])
        
        if dados_animais:
            colunas = ['Código SISBOV', 'Nº Manejo', 'Brinco', 'Categoria', 'Raça', 'Sexo', 'Data Nasc.', 'Status']
            larguras = [2.5*cm, 1.8*cm, 2*cm, 2.5*cm, 2*cm, 1.5*cm, 2*cm, 1.7*cm]
            gerador.criar_tabela_dados(story, dados_animais, colunas, larguras, titulo="INVENTÁRIO DE ANIMAIS")
            
            # Total de animais
            story.append(Paragraph(
                f'<b>Total de Animais Inventariados:</b> {animais.count()}',
                gerador.styles['InfoPropriedade']
            ))
        else:
            story.append(Paragraph('Nenhum animal cadastrado.', gerador.styles['Normal']))
        
        # Declaração de veracidade
        gerador.criar_declaracao_veracidade(story)
        
        # Campo de assinatura
        gerador.criar_campo_assinatura(story, "Responsável Técnico")
        
        # Rodapé oficial
        gerador.criar_rodape_oficial(story)
        
        # Gerar PDF
        return gerador.criar_documento_pdf("Inventario", story)
    
    # Fallback para método antigo se helper não estiver disponível
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_VI_Inventario_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO VI - FORMULÁRIO PARA INVENTÁRIO DE ANIMAIS', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Município:</b> {propriedade.municipio} - {propriedade.uf}', styles['Normal']))
    story.append(Paragraph(f'<b>Data de Emissão:</b> {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Código SISBOV', 'Nº Manejo', 'Brinco', 'Categoria', 'Raça', 'Sexo', 'Data Nasc.', 'Status']]
    for animal in animais:
        dados_tabela.append([
            animal.codigo_sisbov or '—',
            animal.numero_manejo or '—',
            animal.numero_brinco or '—',
            animal.categoria.nome if animal.categoria else '—',
            animal.raca or '—',
            'Fêmea' if animal.sexo == 'F' else 'Macho',
            animal.data_nascimento.strftime('%d/%m/%Y') if animal.data_nascimento else '—',
            animal.get_status_display(),
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[3*cm, 2*cm, 2.5*cm, 3*cm, 2*cm, 1.5*cm, 2*cm, 2*cm])
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
        story.append(Paragraph('Nenhum animal cadastrado.', styles['Normal']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Total de Animais:</b> {animais.count()}', styles['Normal']))
    
    doc.build(story)
    return response


@login_required
def relatorio_sisbov_anexo_vii(request, propriedade_id):
    """
    Anexo VII - Termo de Adesão à Norma Operacional do SISBOV
    """
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_vii_termo_adesao.html', context)


@login_required
def relatorio_sisbov_anexo_vii_pdf(request, propriedade_id):
    """Gera PDF do Anexo VII - Termo de Adesão"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_VII_Termo_Adesao_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    story.append(Paragraph('ANEXO VII - TERMO DE ADESÃO À NORMA OPERACIONAL DO SISBOV', 
                          styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    # Conteúdo do Termo
    story.append(Paragraph('TERMO DE ADESÃO', styles['Heading2']))
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph(
        f'<b>Propriedade:</b> {propriedade.nome_propriedade}<br/>'
        f'<b>Município:</b> {propriedade.municipio} - {propriedade.uf}<br/>'
        f'<b>CNPJ/CPF:</b> {propriedade.produtor.cpf_cnpj if propriedade.produtor else "—"}<br/>'
        f'<b>Data:</b> {date.today().strftime("%d/%m/%Y")}',
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        'Declaro que adiro à Norma Operacional do Sistema Brasileiro de Identificação e '
        'Certificação de Origem Bovina e Bubalina (SISBOV), comprometendo-me a cumprir '
        'todas as exigências estabelecidas na Instrução Normativa MAPA nº 17/2006.',
        styles['Normal']
    ))
    
    doc.build(story)
    return response


@login_required
def relatorio_sisbov_anexo_viii(request, propriedade_id):
    """
    Anexo VIII - Protocolo Declaratório de Produção
    """
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar dados de produção
    animais_ativos = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).count()
    
    animais_por_categoria = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).values('categoria__nome').annotate(
        total=Count('id')
    ).order_by('categoria__nome')
    
    context = {
        'propriedade': propriedade,
        'animais_ativos': animais_ativos,
        'animais_por_categoria': animais_por_categoria,
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_viii_protocolo_producao.html', context)


@login_required
def relatorio_sisbov_anexo_viii_pdf(request, propriedade_id):
    """Gera PDF do Anexo VIII - Protocolo Declaratório de Produção"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_VIII_Protocolo_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    story.append(Paragraph('ANEXO VIII - PROTOCOLO DECLARATÓRIO DE PRODUÇÃO', 
                          styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    # Dados da Propriedade
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Município:</b> {propriedade.municipio} - {propriedade.uf}', styles['Normal']))
    story.append(Paragraph(f'<b>Data:</b> {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Declaração
    story.append(Paragraph(
        'Declaro que as informações fornecidas neste protocolo são verdadeiras e '
        'corretas, assumindo total responsabilidade pela veracidade dos dados declarados.',
        styles['Normal']
    ))
    
    doc.build(story)
    return response


@login_required
def relatorio_sisbov_anexo_xix(request, propriedade_id):
    """
    Anexo XIX - Declaração de Movimentação de Animais
    """
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    # Buscar movimentações recentes (últimos 30 dias)
    data_inicio = date.today() - timedelta(days=30)
    movimentacoes = MovimentacaoIndividual.objects.filter(
        Q(animal__propriedade=propriedade) &
        (Q(propriedade_origem=propriedade) | Q(propriedade_destino=propriedade)),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria', 'propriedade_origem', 'propriedade_destino').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'movimentacoes': movimentacoes,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xix_movimentacao.html', context)


@login_required
def relatorio_sisbov_anexo_xix_pdf(request, propriedade_id):
    """Gera PDF do Anexo XIX - Declaração de Movimentação"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=30)
    movimentacoes = MovimentacaoIndividual.objects.filter(
        Q(animal__propriedade=propriedade) &
        (Q(propriedade_origem=propriedade) | Q(propriedade_destino=propriedade)),
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'propriedade_origem', 'propriedade_destino').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XIX_Movimentacao_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    story.append(Paragraph('ANEXO XIX - DECLARAÇÃO DE MOVIMENTAÇÃO DE ANIMAIS', 
                          styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    # Dados da Propriedade
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Tabela de Movimentações
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Tipo', 'Origem', 'Destino']]
    
    for mov in movimentacoes:
        dados_tabela.append([
            mov.data_movimentacao.strftime('%d/%m/%Y'),
            mov.animal.codigo_sisbov or mov.animal.numero_brinco or '—',
            mov.get_tipo_movimentacao_display(),
            mov.propriedade_origem.nome_propriedade if mov.propriedade_origem else '—',
            mov.propriedade_destino.nome_propriedade if mov.propriedade_destino else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 4*cm, 4*cm])
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
        story.append(Paragraph('Nenhuma movimentação registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO IV - CADASTRO DE PRODUTOR RURAL
# ============================================================================

@login_required
def relatorio_sisbov_anexo_iv(request, propriedade_id):
    """Anexo IV - Cadastro de Produtor Rural"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    produtor = propriedade.produtor
    
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
    produtor = propriedade.produtor
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_IV_Produtor_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO IV - CADASTRO DE PRODUTOR RURAL', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    if produtor:
        story.append(Paragraph(f'<b>Nome:</b> {produtor.nome}', styles['Normal']))
        story.append(Paragraph(f'<b>CPF/CNPJ:</b> {produtor.cpf_cnpj or "—"}', styles['Normal']))
        story.append(Paragraph(f'<b>RG:</b> {produtor.documento_identidade or "—"}', styles['Normal']))
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
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
    
    data_inicio = date.today() - timedelta(days=90)
    nascimentos = []
    
    try:
        from .models_reproducao import Nascimento
        nascimentos = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_inicio
        ).select_related('mae', 'animal_individual').order_by('-data_nascimento')
    except ImportError:
        pass
    
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
    
    try:
        from .models_reproducao import Nascimento
        nascimentos = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_inicio
        ).select_related('mae', 'animal_individual').order_by('-data_nascimento')
    except ImportError:
        pass
    
    nascimentos_mov = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='NASCIMENTO',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XI_Nascimento_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XI - DECLARAÇÃO DE NASCIMENTO', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Bezerro (SISBOV)', 'Mãe (SISBOV)', 'Sexo', 'Peso (kg)', 'Tipo Parto']]
    
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
    
    data_inicio = date.today() - timedelta(days=90)
    mortes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='MORTE',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'mortes': mortes,
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
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
            morte.observacoes or (getattr(morte, 'motivo_detalhado', None) or '—'),
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


# ============================================================================
# ANEXO XIII - DECLARAÇÃO DE PERDA DE BRINCO
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xiii(request, propriedade_id):
    """Anexo XIII - Declaração de Perda de Brinco"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    perdas = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(tipo_movimentacao='OUTROS') | 
        Q(observacoes__icontains='perda') |
        Q(observacoes__icontains='brinco')
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'perdas': perdas,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xiii_perda_brinco.html', context)


@login_required
def relatorio_sisbov_anexo_xiii_pdf(request, propriedade_id):
    """Gera PDF do Anexo XIII - Declaração de Perda de Brinco"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    perdas = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(tipo_movimentacao='OUTROS') | 
        Q(observacoes__icontains='perda') |
        Q(observacoes__icontains='brinco')
    ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XIII_Perda_Brinco_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XIII - DECLARAÇÃO DE PERDA DE BRINCO', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Brinco Perdido', 'Observações']]
    for perda in perdas:
        dados_tabela.append([
            perda.data_movimentacao.strftime('%d/%m/%Y'),
            perda.animal.codigo_sisbov or perda.animal.numero_brinco or '—',
            perda.animal.numero_brinco or '—',
            perda.observacoes or '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 6*cm])
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
        story.append(Paragraph('Nenhuma perda de brinco registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XIV - DECLARAÇÃO DE MUDANÇA DE CATEGORIA
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xiv(request, propriedade_id):
    """Anexo XIV - Declaração de Mudança de Categoria"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    mudancas = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='MUDANCA_CATEGORIA',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria', 'categoria_anterior', 'categoria_nova').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'mudancas': mudancas,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xiv_mudanca_categoria.html', context)


@login_required
def relatorio_sisbov_anexo_xiv_pdf(request, propriedade_id):
    """Gera PDF do Anexo XIV - Declaração de Mudança de Categoria"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    mudancas = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='MUDANCA_CATEGORIA',
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'categoria_anterior', 'categoria_nova').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XIV_Mudanca_Categoria_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XIV - DECLARAÇÃO DE MUDANÇA DE CATEGORIA', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Categoria Anterior', 'Categoria Nova', 'Peso (kg)']]
    for mudanca in mudancas:
        dados_tabela.append([
            mudanca.data_movimentacao.strftime('%d/%m/%Y'),
            mudanca.animal.codigo_sisbov or mudanca.animal.numero_brinco or '—',
            mudanca.categoria_anterior.nome if mudanca.categoria_anterior else '—',
            mudanca.categoria_nova.nome if mudanca.categoria_nova else '—',
            str(mudanca.peso_kg) if mudanca.peso_kg else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 3*cm, 3*cm, 2*cm])
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
        story.append(Paragraph('Nenhuma mudança de categoria registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XV - DECLARAÇÃO DE MUDANÇA DE PROPRIEDADE
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xv(request, propriedade_id):
    """Anexo XV - Declaração de Mudança de Propriedade"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    mudancas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_origem=propriedade) | Q(propriedade_destino=propriedade),
        tipo_movimentacao__in=['TRANSFERENCIA_ENTRADA', 'TRANSFERENCIA_SAIDA', 'COMPRA', 'VENDA'],
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'animal__categoria', 'propriedade_origem', 'propriedade_destino').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'mudancas': mudancas,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xv_mudanca_propriedade.html', context)


@login_required
def relatorio_sisbov_anexo_xv_pdf(request, propriedade_id):
    """Gera PDF do Anexo XV - Declaração de Mudança de Propriedade"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    mudancas = MovimentacaoIndividual.objects.filter(
        Q(propriedade_origem=propriedade) | Q(propriedade_destino=propriedade),
        tipo_movimentacao__in=['TRANSFERENCIA_ENTRADA', 'TRANSFERENCIA_SAIDA', 'COMPRA', 'VENDA'],
        data_movimentacao__gte=data_inicio
    ).select_related('animal', 'propriedade_origem', 'propriedade_destino').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XV_Mudanca_Propriedade_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XV - DECLARAÇÃO DE MUDANÇA DE PROPRIEDADE', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Tipo', 'Origem', 'Destino', 'Peso (kg)']]
    for mudanca in mudancas:
        dados_tabela.append([
            mudanca.data_movimentacao.strftime('%d/%m/%Y'),
            mudanca.animal.codigo_sisbov or mudanca.animal.numero_brinco or '—',
            mudanca.get_tipo_movimentacao_display(),
            mudanca.propriedade_origem.nome_propriedade if mudanca.propriedade_origem else '—',
            mudanca.propriedade_destino.nome_propriedade if mudanca.propriedade_destino else '—',
            str(mudanca.peso_kg) if mudanca.peso_kg else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm, 3*cm, 2*cm])
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
        story.append(Paragraph('Nenhuma mudança de propriedade registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XVI - DECLARAÇÃO DE ABATE
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xvi(request, propriedade_id):
    """Anexo XVI - Declaração de Abate"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    abates = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='VENDA',
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='abate') | 
        Q(observacoes__icontains='frigorífico') |
        Q(observacoes__icontains='frigorifico')
    ).select_related('animal', 'animal__categoria', 'propriedade_destino').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'abates': abates,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xvi_abate.html', context)


@login_required
def relatorio_sisbov_anexo_xvi_pdf(request, propriedade_id):
    """Gera PDF do Anexo XVI - Declaração de Abate"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=90)
    abates = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='VENDA',
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='abate') | 
        Q(observacoes__icontains='frigorífico') |
        Q(observacoes__icontains='frigorifico')
    ).select_related('animal', 'propriedade_destino').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XVI_Abate_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XVI - DECLARAÇÃO DE ABATE', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Categoria', 'Destino', 'Peso (kg)', 'Valor (R$)']]
    for abate in abates:
        dados_tabela.append([
            abate.data_movimentacao.strftime('%d/%m/%Y'),
            abate.animal.codigo_sisbov or abate.animal.numero_brinco or '—',
            abate.animal.categoria.nome if abate.animal.categoria else '—',
            abate.propriedade_destino.nome_propriedade if abate.propriedade_destino else '—',
            str(abate.peso_kg) if abate.peso_kg else '—',
            f'R$ {abate.valor:.2f}' if abate.valor else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm, 2*cm, 2*cm])
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
        story.append(Paragraph('Nenhum abate registrado no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XVII - DECLARAÇÃO DE EXPORTAÇÃO
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xvii(request, propriedade_id):
    """Anexo XVII - Declaração de Exportação"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    exportacoes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='VENDA',
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='exportação') | 
        Q(observacoes__icontains='exportacao')
    ).select_related('animal', 'animal__categoria', 'propriedade_destino').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'exportacoes': exportacoes,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xvii_exportacao.html', context)


@login_required
def relatorio_sisbov_anexo_xvii_pdf(request, propriedade_id):
    """Gera PDF do Anexo XVII - Declaração de Exportação"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    exportacoes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade,
        tipo_movimentacao='VENDA',
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='exportação') | 
        Q(observacoes__icontains='exportacao')
    ).select_related('animal', 'propriedade_destino').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XVII_Exportacao_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XVII - DECLARAÇÃO DE EXPORTAÇÃO', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Destino', 'Peso (kg)', 'Valor (R$)']]
    for exp in exportacoes:
        dados_tabela.append([
            exp.data_movimentacao.strftime('%d/%m/%Y'),
            exp.animal.codigo_sisbov or exp.animal.numero_brinco or '—',
            exp.propriedade_destino.nome_propriedade if exp.propriedade_destino else '—',
            str(exp.peso_kg) if exp.peso_kg else '—',
            f'R$ {exp.valor:.2f}' if exp.valor else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 4*cm, 2*cm, 2.5*cm])
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
        story.append(Paragraph('Nenhuma exportação registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response


# ============================================================================
# ANEXO XVIII - DECLARAÇÃO DE IMPORTAÇÃO
# ============================================================================

@login_required
def relatorio_sisbov_anexo_xviii(request, propriedade_id):
    """Anexo XVIII - Declaração de Importação"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    importacoes = MovimentacaoIndividual.objects.filter(
        Q(propriedade_destino=propriedade) | Q(animal__propriedade=propriedade),
        tipo_movimentacao__in=['COMPRA', 'TRANSFERENCIA_ENTRADA'],
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='importação') | 
        Q(observacoes__icontains='importacao')
    ).select_related('animal', 'animal__categoria', 'propriedade_origem').order_by('-data_movimentacao')
    
    context = {
        'propriedade': propriedade,
        'importacoes': importacoes,
        'data_inicio': data_inicio,
        'data_fim': date.today(),
        'data_emissao': date.today(),
    }
    
    return render(request, 'gestao_rural/relatorios_sisbov/anexo_xviii_importacao.html', context)


@login_required
def relatorio_sisbov_anexo_xviii_pdf(request, propriedade_id):
    """Gera PDF do Anexo XVIII - Declaração de Importação"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    data_inicio = date.today() - timedelta(days=180)
    importacoes = MovimentacaoIndividual.objects.filter(
        Q(propriedade_destino=propriedade) | Q(animal__propriedade=propriedade),
        tipo_movimentacao__in=['COMPRA', 'TRANSFERENCIA_ENTRADA'],
        data_movimentacao__gte=data_inicio
    ).filter(
        Q(observacoes__icontains='importação') | 
        Q(observacoes__icontains='importacao')
    ).select_related('animal', 'propriedade_origem').order_by('-data_movimentacao')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SISBOV_Anexo_XVIII_Importacao_{propriedade.id}_{date.today().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph('ANEXO XVIII - DECLARAÇÃO DE IMPORTAÇÃO', styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f'<b>Propriedade:</b> {propriedade.nome_propriedade}', styles['Normal']))
    story.append(Paragraph(f'<b>Período:</b> {data_inicio.strftime("%d/%m/%Y")} a {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [['Data', 'Animal (SISBOV)', 'Origem', 'Peso (kg)', 'Valor (R$)']]
    for imp in importacoes:
        dados_tabela.append([
            imp.data_movimentacao.strftime('%d/%m/%Y'),
            imp.animal.codigo_sisbov or imp.animal.numero_brinco or '—',
            imp.propriedade_origem.nome_propriedade if imp.propriedade_origem else '—',
            str(imp.peso_kg) if imp.peso_kg else '—',
            f'R$ {imp.valor:.2f}' if imp.valor else '—',
        ])
    
    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, colWidths=[2.5*cm, 3.5*cm, 4*cm, 2*cm, 2.5*cm])
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
        story.append(Paragraph('Nenhuma importação registrada no período.', styles['Normal']))
    
    doc.build(story)
    return response

