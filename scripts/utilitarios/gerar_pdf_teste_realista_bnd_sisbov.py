# -*- coding: utf-8 -*-
"""
Script para gerar PDF de teste BND SISBOV REALISTA
Usa animais reais cadastrados no sistema e introduz divergências intencionais:
- 5% com dados faltantes (sexo, raça ou data de nascimento)
- 1% não conforme (animais no sistema mas não no PDF, e vice-versa)
- 94% corretos
"""

import os
import sys
import django
import random
from datetime import date, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Tentar diferentes configurações de settings
settings_modules = [
    'sistema_rural.settings',  # Configuração do manage.py na raiz
    'monpec_sistema_completo.monpec_sistema_completo.settings',
    'monpec_sistema.settings',
]

settings_ok = False
for settings_module in settings_modules:
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
        django.setup()
        settings_ok = True
        print(f"[INFO] Django configurado com: {settings_module}")
        break
    except Exception as e:
        continue

if not settings_ok:
    print("[ERRO] Nao foi possivel configurar Django. Verifique o settings.py")
    sys.exit(1)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from gestao_rural.models import AnimalIndividual, Propriedade

def gerar_codigo_sisbov_fake():
    """Gera um código SISBOV fake para animais que não estão no sistema"""
    numero = ''.join([str(random.randint(0, 9)) for _ in range(13)])
    return f"BR{numero}"

def gerar_numero_brinco_fake():
    """Gera um número de brinco fake"""
    return ''.join([str(random.randint(0, 9)) for _ in range(15)])

def criar_pdf_teste_realista_bnd_sisbov(propriedade_id, nome_arquivo='teste_realista_bnd_sisbov.pdf'):
    """Cria um PDF de teste realista com animais reais e divergências"""
    
    # Buscar propriedade
    try:
        propriedade = Propriedade.objects.get(pk=propriedade_id)
    except Propriedade.DoesNotExist:
        print(f"[ERRO] Propriedade com ID {propriedade_id} nao encontrada!")
        return None
    
    # Buscar animais ativos da propriedade
    animais_reais = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).select_related('categoria').order_by('codigo_sisbov', 'numero_brinco')
    
    total_animais = animais_reais.count()
    
    if total_animais == 0:
        print(f"[ERRO] Nenhum animal ativo encontrado na propriedade {propriedade.nome_propriedade}!")
        return None
    
    print(f"\n[INFO] Propriedade: {propriedade.nome_propriedade}")
    print(f"[INFO] Total de animais encontrados: {total_animais}")
    
    # Calcular quantidades para divergências
    animais_com_dados_faltantes = max(1, int(total_animais * 0.05))  # 5%
    animais_nao_conformes = max(1, int(total_animais * 0.01))  # 1%
    animais_corretos = total_animais - animais_com_dados_faltantes - animais_nao_conformes  # Restante
    
    print(f"[INFO] Distribuicao de divergencias:")
    print(f"  - Animais corretos: {animais_corretos} (94%)")
    print(f"  - Com dados faltantes: {animais_com_dados_faltantes} (5%)")
    print(f"  - Nao conformes: {animais_nao_conformes} (1%)")
    
    # Converter animais para lista
    lista_animais = list(animais_reais)
    random.shuffle(lista_animais)  # Embaralhar para distribuição aleatória
    
    # Preparar dados para PDF
    animais_pdf = []
    animais_nao_no_pdf = []  # Animais que estão no sistema mas não no PDF
    animais_so_no_pdf = []  # Animais que estão no PDF mas não no sistema
    
    # Processar animais corretos (94%)
    for i in range(animais_corretos):
        if i < len(lista_animais):
            animal = lista_animais[i]
            animais_pdf.append({
                'animal_obj': animal,
                'tipo': 'correto',
                'codigo_sisbov': animal.codigo_sisbov or animal.numero_brinco or '',
                'numero_manejo': animal.numero_manejo or (animal.codigo_sisbov[-6:] if animal.codigo_sisbov and len(animal.codigo_sisbov) >= 6 else ''),
                'numero_brinco': animal.numero_brinco or '',
                'raca': animal.raca or '',
                'sexo': animal.sexo if animal.sexo else '',
                'data_nascimento': animal.data_nascimento,
                'peso_kg': animal.peso_atual_kg,
            })
    
    # Processar animais com dados faltantes (5%)
    inicio_faltantes = animais_corretos
    fim_faltantes = inicio_faltantes + animais_com_dados_faltantes
    
    for i in range(inicio_faltantes, fim_faltantes):
        if i < len(lista_animais):
            animal = lista_animais[i]
            # Escolher aleatoriamente qual dado faltar
            tipo_falta = random.choice(['sexo', 'raca', 'data_nascimento'])
            
            animal_pdf = {
                'animal_obj': animal,
                'tipo': 'dados_faltantes',
                'codigo_sisbov': animal.codigo_sisbov or animal.numero_brinco or '',
                'numero_manejo': animal.numero_manejo or (animal.codigo_sisbov[-6:] if animal.codigo_sisbov and len(animal.codigo_sisbov) >= 6 else ''),
                'numero_brinco': animal.numero_brinco or '',
                'raca': animal.raca or '',
                'sexo': animal.sexo if animal.sexo else '',
                'data_nascimento': animal.data_nascimento,
                'peso_kg': animal.peso_atual_kg,
                'dado_faltante': tipo_falta,
            }
            
            # Remover o dado escolhido
            if tipo_falta == 'sexo':
                animal_pdf['sexo'] = ''
            elif tipo_falta == 'raca':
                animal_pdf['raca'] = ''
            elif tipo_falta == 'data_nascimento':
                animal_pdf['data_nascimento'] = None
            
            animais_pdf.append(animal_pdf)
    
    # Processar animais não conformes (1%)
    # Alguns animais do sistema não estarão no PDF
    inicio_nao_conformes = fim_faltantes
    fim_nao_conformes = inicio_nao_conformes + animais_nao_conformes
    
    for i in range(inicio_nao_conformes, fim_nao_conformes):
        if i < len(lista_animais):
            # Metade: animais no sistema mas não no PDF
            if i < inicio_nao_conformes + (animais_nao_conformes // 2):
                animais_nao_no_pdf.append(lista_animais[i])
            else:
                # Metade: animais no PDF mas não no sistema (criar fake)
                animais_so_no_pdf.append({
                    'codigo_sisbov': gerar_codigo_sisbov_fake(),
                    'numero_manejo': ''.join([str(random.randint(0, 9)) for _ in range(6)]),
                    'numero_brinco': gerar_numero_brinco_fake(),
                    'raca': random.choice(['Nelore', 'Angus', 'Brahman', 'Brangus', 'Hereford']),
                    'sexo': random.choice(['M', 'F']),
                    'data_nascimento': date.today() - timedelta(days=random.randint(100, 1000)),
                    'peso_kg': random.randint(200, 600),
                    'tipo': 'so_no_pdf',
                })
                animais_pdf.append(animais_so_no_pdf[-1])
    
    # Embaralhar novamente para misturar os tipos
    random.shuffle(animais_pdf)
    
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
    
    # Informações da Propriedade (IDÊNTICAS ao sistema)
    story.append(Paragraph('DADOS DO ESTABELECIMENTO RURAL', subtitulo_style))
    
    # Usar dados reais da propriedade
    cnpj_cpf = propriedade.produtor.cpf_cnpj if propriedade.produtor else ''
    nome_propriedade = propriedade.nome_propriedade
    
    dados_propriedade = [
        ['Propriedade:', nome_propriedade],
        ['CNPJ/CPF:', cnpj_cpf],
        ['Inscrição Estadual:', propriedade.inscricao_estadual or ''],
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
    
    # Adicionar animais ao PDF
    for animal_data in animais_pdf:
        # Formatar dados
        codigo_sisbov = animal_data.get('codigo_sisbov', '') or ''
        numero_manejo = animal_data.get('numero_manejo', '') or ''
        numero_brinco = animal_data.get('numero_brinco', '') or ''
        raca = animal_data.get('raca', '') or ''
        sexo = animal_data.get('sexo', '') or ''
        
        # Formatar sexo
        if sexo == 'M':
            sexo_display = 'Macho'
        elif sexo == 'F':
            sexo_display = 'Fêmea'
        else:
            sexo_display = ''
        
        # Formatar data
        data_nasc = animal_data.get('data_nascimento')
        if data_nasc:
            if isinstance(data_nasc, date):
                data_nasc_str = data_nasc.strftime('%d/%m/%Y')
            else:
                data_nasc_str = str(data_nasc)
        else:
            data_nasc_str = ''
        
        # Formatar peso
        peso = animal_data.get('peso_kg')
        if peso:
            peso_str = str(int(peso)) if isinstance(peso, (int, float)) else str(peso)
        else:
            peso_str = ''
        
        dados_tabela.append([
            codigo_sisbov,
            numero_manejo,
            numero_brinco,
            raca,
            sexo_display,
            data_nasc_str,
            peso_str
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
    story.append(Paragraph(f'<b>Total de Animais no PDF:</b> {len(animais_pdf)}', styles['Normal']))
    story.append(Spacer(1, 0.3*cm))
    
    # Informações sobre divergências (para documentação)
    story.append(Paragraph('<b>Nota:</b> Este PDF contém divergências intencionais para teste:', styles['Normal']))
    story.append(Paragraph(f'- {animais_corretos} animais corretos (94%)', styles['Normal']))
    story.append(Paragraph(f'- {animais_com_dados_faltantes} animais com dados faltantes (5%)', styles['Normal']))
    story.append(Paragraph(f'- {animais_nao_conformes} animais não conformes (1%)', styles['Normal']))
    story.append(Spacer(1, 0.3*cm))
    
    if animais_nao_no_pdf:
        story.append(Paragraph(f'<b>Animais no sistema mas NÃO no PDF:</b> {len(animais_nao_no_pdf)}', styles['Normal']))
        for animal in animais_nao_no_pdf[:5]:  # Mostrar apenas os 5 primeiros
            codigo = animal.codigo_sisbov or animal.numero_brinco or 'N/A'
            story.append(Paragraph(f'  - {codigo}', styles['Normal']))
        if len(animais_nao_no_pdf) > 5:
            story.append(Paragraph(f'  ... e mais {len(animais_nao_no_pdf) - 5} animais', styles['Normal']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f'Documento gerado em {date.today().strftime("%d/%m/%Y")} - Teste Realista BND SISBOV',
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(story)
    
    print(f"\n[OK] PDF de teste realista criado: {nome_arquivo}")
    print(f"   Total de animais no PDF: {len(animais_pdf)}")
    print(f"   Animais corretos: {animais_corretos}")
    print(f"   Animais com dados faltantes: {animais_com_dados_faltantes}")
    print(f"   Animais nao conformes: {animais_nao_conformes}")
    print(f"   Animais no sistema mas NAO no PDF: {len(animais_nao_no_pdf)}")
    print(f"   Animais so no PDF (fakes): {len(animais_so_no_pdf)}")
    
    # Salvar relatório de divergências
    relatorio_nome = nome_arquivo.replace('.pdf', '_divergencias.txt')
    with open(relatorio_nome, 'w', encoding='utf-8') as f:
        f.write("RELATORIO DE DIVERGENCIAS - TESTE REALISTA BND SISBOV\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Propriedade: {nome_propriedade}\n")
        f.write(f"Data: {date.today().strftime('%d/%m/%Y')}\n\n")
        f.write(f"Total de animais no sistema: {total_animais}\n")
        f.write(f"Total de animais no PDF: {len(animais_pdf)}\n\n")
        f.write("DIVERGENCIAS INTENCIONAIS:\n")
        f.write("-" * 60 + "\n\n")
        
        f.write(f"1. ANIMAIS COM DADOS FALTANTES ({animais_com_dados_faltantes}):\n")
        for animal_data in animais_pdf:
            if animal_data.get('tipo') == 'dados_faltantes':
                codigo = animal_data.get('codigo_sisbov', 'N/A')
                dado_faltante = animal_data.get('dado_faltante', 'N/A')
                f.write(f"   - {codigo}: Falta {dado_faltante}\n")
        
        f.write(f"\n2. ANIMAIS NO SISTEMA MAS NAO NO PDF ({len(animais_nao_no_pdf)}):\n")
        for animal in animais_nao_no_pdf:
            codigo = animal.codigo_sisbov or animal.numero_brinco or 'N/A'
            f.write(f"   - {codigo}\n")
        
        f.write(f"\n3. ANIMAIS SO NO PDF (FAKES) ({len(animais_so_no_pdf)}):\n")
        for animal_data in animais_so_no_pdf:
            codigo = animal_data.get('codigo_sisbov', 'N/A')
            f.write(f"   - {codigo}\n")
    
    print(f"   Relatorio de divergencias salvo: {relatorio_nome}")
    
    return nome_arquivo

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python gerar_pdf_teste_realista_bnd_sisbov.py <propriedade_id> [nome_arquivo]")
        print("\nExemplo:")
        print("  python gerar_pdf_teste_realista_bnd_sisbov.py 1")
        print("  python gerar_pdf_teste_realista_bnd_sisbov.py 1 teste_realista.pdf")
        sys.exit(1)
    
    propriedade_id = int(sys.argv[1])
    nome_arquivo = sys.argv[2] if len(sys.argv) > 2 else 'teste_realista_bnd_sisbov.pdf'
    
    criar_pdf_teste_realista_bnd_sisbov(propriedade_id, nome_arquivo)


