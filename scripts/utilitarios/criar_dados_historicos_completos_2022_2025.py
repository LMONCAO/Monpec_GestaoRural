#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar dados históricos completos de 2022 a 2025
Inclui: Rebanho, Bens Imobilizados, Pagamentos, Dívidas SCR, Receitas e Despesas
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date, timedelta
from random import randint, choice, uniform

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    MovimentacaoProjetada, BemImobilizado
)
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira, ReceitaAnual
)
from gestao_rural.models_cadastros import Cliente, FornecedorCadastro

# Valores de referência do SCR
DIVIDA_INICIAL_2022 = Decimal('14000000.00')  # R$ 14 milhões
PAGAMENTO_TRIMESTRAL = Decimal('1500000.00')  # R$ 1,5 milhão a cada 3 meses
PAGAMENTO_AVALISTA_OUT_2024 = Decimal('2478000.00')  # R$ 2,478 milhões
SALDO_LIQUIDO_ANUAL = Decimal('1700000.00')  # R$ 1,7 milhão (média entre 1,5 e 1,9)

# Queda de preços em 2023 (baseado em indicadores de mercado)
FATOR_QUEDA_2023 = Decimal('0.75')  # 25% de queda
FATOR_RECUPERACAO_2024 = Decimal('0.90')  # Recuperação parcial
FATOR_RECUPERACAO_2025 = Decimal('1.05')  # Acima do normal


def criar_rebanho_historico(propriedades, ano_inicio, ano_fim):
    """Cria inventários de rebanho ao longo dos anos"""
    print("=" * 80)
    print(f"CRIANDO REBANHO HISTÓRICO - {ano_inicio} a {ano_fim}")
    print("=" * 80)
    print()
    
    # Buscar categorias (priorizar as corretas)
    todas_categorias = CategoriaAnimal.objects.all()
    
    categorias = {}
    for cat in todas_categorias:
        nome_lower = cat.nome.lower()
        nome_original = cat.nome
        
        # Vacas em Reprodução (priorizar, não descarte)
        if 'vaca' in nome_lower and ('reprodução' in nome_lower or 'reproducao' in nome_lower) and 'descarte' not in nome_lower:
            if 'vaca' not in categorias or 'descarte' in categorias.get('vaca', CategoriaAnimal()).nome.lower():
                categorias['vaca'] = cat
        # Se não encontrou, aceitar qualquer vaca com +36
        elif 'vaca' in nome_lower and ('+36' in nome_original or '36' in nome_lower) and 'vaca' not in categorias:
            categorias['vaca'] = cat
        
        # Primíparas
        if ('primípara' in nome_lower or 'primipara' in nome_lower) and 'primipara' not in categorias:
            categorias['primipara'] = cat
        
        # Bezerros (machos)
        if 'bezerro' in nome_lower and 'bezerra' not in nome_lower and 'bezerro' not in categorias:
            categorias['bezerro'] = cat
        
        # Bezerras (fêmeas)
        if 'bezerra' in nome_lower and 'bezerra' not in categorias:
            categorias['bezerra'] = cat
        
        # Garrotes
        if 'garrote' in nome_lower and 'garrote' not in categorias:
            categorias['garrote'] = cat
        
        # Bois (não gordo)
        if 'boi' in nome_lower and 'gordo' not in nome_lower and ('24-36' in nome_original or '24' in nome_lower) and 'boi' not in categorias:
            categorias['boi'] = cat
    
    print(f"[INFO] Categorias encontradas: {len(categorias)}")
    for key, cat in categorias.items():
        print(f"  - {key}: {cat.nome}")
    print()
    
    # Valores por cabeça (baseados em mercado)
    valores_por_categoria = {
        'vaca': Decimal('5200.00'),
        'primipara': Decimal('4500.00'),
        'bezerro': Decimal('2200.00'),
        'bezerra': Decimal('1500.00'),
        'garrote': Decimal('2800.00'),
        'boi': Decimal('4200.00'),
    }
    
    # Evolução do rebanho (crescimento ao longo dos anos)
    rebanho_base = {
        'vaca': 4800,
        'primipara': 1173,
        'bezerro': 2000,
        'bezerra': 2000,
        'garrote': 1500,
        'boi': 1200,
    }
    
    inventarios_criados = []
    
    for ano in range(ano_inicio, ano_fim + 1):
        # Ajustar valores por categoria conforme ano (queda em 2023)
        fator_preco = Decimal('1.00')
        if ano == 2023:
            fator_preco = FATOR_QUEDA_2023
        elif ano == 2024:
            fator_preco = FATOR_RECUPERACAO_2024
        elif ano == 2025:
            fator_preco = FATOR_RECUPERACAO_2025
        
        # Crescimento do rebanho ao longo dos anos
        fator_crescimento = Decimal(str(1.0 + (ano - ano_inicio) * 0.05))  # 5% ao ano
        
        for propriedade in propriedades:
            # Focar na Fazenda Canta Galo (matriz)
            if 'Canta Galo' in propriedade.nome_propriedade:
                for cat_key in rebanho_base.keys():
                    categoria = categorias.get(cat_key)
                    if categoria:
                        quantidade = int(rebanho_base[cat_key] * fator_crescimento)
                        valor_unitario = valores_por_categoria[cat_key] * fator_preco
                        
                        # Criar inventário (usar update_or_create para atualizar se existir)
                        inventario, created = InventarioRebanho.objects.update_or_create(
                            propriedade=propriedade,
                            categoria=categoria,
                            data_inventario=date(ano, 1, 1),
                            defaults={
                                'quantidade': quantidade,
                                'valor_por_cabeca': valor_unitario,
                            }
                        )
                        
                        inventarios_criados.append(inventario)
                        valor_total = inventario.valor_total
                        if created:
                            print(f"[OK] Inventário {ano} CRIADO: {propriedade.nome_propriedade} - {quantidade} {categoria.nome} - R$ {valor_total:,.2f}")
                        else:
                            print(f"[OK] Inventário {ano} ATUALIZADO: {propriedade.nome_propriedade} - {quantidade} {categoria.nome} - R$ {valor_total:,.2f}")
    
    print()
    print(f"Total de inventários criados: {len(inventarios_criados)}")
    print()
    
    return inventarios_criados


def criar_bens_imobilizados(propriedades):
    """Cria bens imobilizados para as propriedades"""
    print("=" * 80)
    print("CRIANDO BENS IMOBILIZADOS")
    print("=" * 80)
    print()
    
    from gestao_rural.models import CategoriaImobilizado
    
    # Buscar ou criar categorias
    categoria_maquinario, _ = CategoriaImobilizado.objects.get_or_create(
        nome='Maquinário Agrícola',
        defaults={
            'vida_util_anos': 10,
            'taxa_depreciacao': Decimal('10.00')  # 10% ao ano
        }
    )
    
    categoria_infraestrutura, _ = CategoriaImobilizado.objects.get_or_create(
        nome='Infraestrutura',
        defaults={
            'vida_util_anos': 20,
            'taxa_depreciacao': Decimal('5.00')  # 5% ao ano
        }
    )
    
    categoria_veiculo, _ = CategoriaImobilizado.objects.get_or_create(
        nome='Veículos',
        defaults={
            'vida_util_anos': 5,
            'taxa_depreciacao': Decimal('20.00')  # 20% ao ano
        }
    )
    
    bens_data = [
        {'nome': 'Trator John Deere 6110J', 'valor': Decimal('450000.00'), 'data': date(2020, 3, 15), 'categoria': categoria_maquinario},
        {'nome': 'Colheitadeira Case IH', 'valor': Decimal('1200000.00'), 'data': date(2021, 6, 10), 'categoria': categoria_maquinario},
        {'nome': 'Plantadeira 16 linhas', 'valor': Decimal('280000.00'), 'data': date(2020, 2, 20), 'categoria': categoria_maquinario},
        {'nome': 'Pulverizador autopropelido', 'valor': Decimal('380000.00'), 'data': date(2021, 4, 5), 'categoria': categoria_maquinario},
        {'nome': 'Caminhão Volvo', 'valor': Decimal('320000.00'), 'data': date(2019, 8, 12), 'categoria': categoria_veiculo},
        {'nome': 'Silos de armazenamento', 'valor': Decimal('150000.00'), 'data': date(2020, 11, 8), 'categoria': categoria_infraestrutura},
        {'nome': 'Galpões e estruturas', 'valor': Decimal('800000.00'), 'data': date(2018, 5, 20), 'categoria': categoria_infraestrutura},
        {'nome': 'Cercas e benfeitorias', 'valor': Decimal('450000.00'), 'data': date(2019, 3, 10), 'categoria': categoria_infraestrutura},
    ]
    
    bens_criados = []
    
    for propriedade in propriedades:
        if 'Canta Galo' in propriedade.nome_propriedade:
            for bem_data in bens_data:
                bem, created = BemImobilizado.objects.update_or_create(
                    propriedade=propriedade,
                    nome=bem_data['nome'],
                    defaults={
                        'categoria': bem_data['categoria'],
                        'valor_aquisicao': bem_data['valor'],
                        'data_aquisicao': bem_data['data'],
                        'data_inicio_depreciacao': bem_data['data'],
                        'ativo': True,
                    }
                )
                bens_criados.append(bem)
                if created:
                    print(f"[OK] Bem criado: {bem.nome} - R$ {bem.valor_aquisicao:,.2f}")
                else:
                    print(f"[OK] Bem atualizado: {bem.nome} - R$ {bem.valor_aquisicao:,.2f}")
    
    print()
    print(f"Total de bens criados: {len(bens_criados)}")
    print()
    
    return bens_criados


def criar_pagamentos_trimestrais(propriedades, ano_inicio, ano_fim):
    """Cria pagamentos trimestrais de R$ 1,5 milhão da Fazenda Canta Galo"""
    print("=" * 80)
    print(f"CRIANDO PAGAMENTOS TRIMESTRAIS - {ano_inicio} a {ano_fim}")
    print("=" * 80)
    print()
    
    # Buscar categoria de despesa
    categoria_pagamento, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento de Financiamento',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Pagamento de financiamento da propriedade'}
    )
    
    pagamentos_criados = []
    
    canta_galo = propriedades.filter(nome_propriedade__icontains='Canta Galo').first()
    if not canta_galo:
        print("[ERRO] Fazenda Canta Galo não encontrada!")
        return []
    
    # Pagamentos a cada 3 meses (janeiro, abril, julho, outubro)
    meses_pagamento = [1, 4, 7, 10]
    
    for ano in range(ano_inicio, ano_fim + 1):
        for mes in meses_pagamento:
            # Não criar pagamentos futuros
            if ano == ano_fim and mes > 10:  # Até outubro de 2025
                continue
            
            data_pagamento = date(ano, mes, 15)
            
            lancamento = LancamentoFinanceiro.objects.create(
                propriedade=canta_galo,
                categoria=categoria_pagamento,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'Pagamento trimestral de financiamento - {mes}/{ano}',
                valor=PAGAMENTO_TRIMESTRAL,
                data_competencia=data_pagamento,
                data_vencimento=data_pagamento,
                data_quitacao=data_pagamento,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            
            pagamentos_criados.append(lancamento)
            print(f"[OK] Pagamento criado: {mes:02d}/{ano} - R$ {PAGAMENTO_TRIMESTRAL:,.2f}")
    
    print()
    print(f"Total de pagamentos trimestrais criados: {len(pagamentos_criados)}")
    print()
    
    return pagamentos_criados


def criar_pagamento_avalista_out_2024(propriedades):
    """Cria pagamento de avalista em outubro de 2024"""
    print("=" * 80)
    print("CRIANDO PAGAMENTO DE AVALISTA - OUTUBRO/2024")
    print("=" * 80)
    print()
    
    categoria_avalista, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento como Avalista',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Pagamento de dívidas como avalista (SCR)'}
    )
    
    canta_galo = propriedades.filter(nome_propriedade__icontains='Canta Galo').first()
    if not canta_galo:
        print("[ERRO] Fazenda Canta Galo não encontrada!")
        return None
    
    data_pagamento = date(2024, 10, 15)
    
    lancamento = LancamentoFinanceiro.objects.create(
        propriedade=canta_galo,
        categoria=categoria_avalista,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        descricao=f'Pagamento como avalista - Renegociação de dívidas SCR - Out/2024',
        valor=PAGAMENTO_AVALISTA_OUT_2024,
        data_competencia=data_pagamento,
        data_vencimento=data_pagamento,
        data_quitacao=data_pagamento,
        status=LancamentoFinanceiro.STATUS_QUITADO,
    )
    
    print(f"[OK] Pagamento de avalista criado: Out/2024 - R$ {PAGAMENTO_AVALISTA_OUT_2024:,.2f}")
    print()
    
    return lancamento


def criar_receitas_despesas_historicas(propriedades, ano_inicio, ano_fim):
    """Cria receitas e despesas históricas com queda em 2023"""
    print("=" * 80)
    print(f"CRIANDO RECEITAS E DESPESAS HISTÓRICAS - {ano_inicio} a {ano_fim}")
    print("=" * 80)
    print()
    
    # Buscar categorias
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Receita com vendas de gado'}
    )
    
    categoria_despesa_operacional, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Despesas Operacionais',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Despesas operacionais da propriedade'}
    )
    
    # Receita base anual (ajustada por ano)
    receitas_base_anual = {
        2022: Decimal('28000000.00'),  # R$ 28 milhões
        2023: Decimal('21000000.00'),  # R$ 21 milhões (queda de 25%)
        2024: Decimal('25200000.00'),  # R$ 25,2 milhões (recuperação)
        2025: Decimal('29400000.00'),  # R$ 29,4 milhões (acima do normal)
    }
    
    # Despesas base (proporcionais à receita)
    lancamentos_criados = []
    
    for ano in range(ano_inicio, ano_fim + 1):
        receita_anual = receitas_base_anual.get(ano, receitas_base_anual[2022])
        receita_mensal = receita_anual / Decimal('12')
        
        # Despesas operacionais (60% da receita)
        despesa_anual = receita_anual * Decimal('0.60')
        despesa_mensal = despesa_anual / Decimal('12')
        
        # Calcular saldo líquido desejado
        saldo_liquido_desejado = SALDO_LIQUIDO_ANUAL
        if ano == 2023:
            saldo_liquido_desejado = Decimal('1200000.00')  # Menor em 2023
        elif ano == 2024:
            saldo_liquido_desejado = Decimal('1500000.00')
        elif ano == 2025:
            saldo_liquido_desejado = Decimal('1900000.00')
        
        # Ajustar despesas para atingir saldo líquido desejado
        despesa_ajustada = receita_anual - saldo_liquido_desejado
        despesa_mensal_ajustada = despesa_ajustada / Decimal('12')
        
        for propriedade in propriedades:
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:  # Até outubro de 2025
                    continue
                
                data_competencia = date(ano, mes, 15)
                
                # Receita mensal (maior concentração no 2º semestre)
                if mes >= 7:
                    fator_mes = Decimal('1.15')  # 15% acima da média no 2º semestre
                else:
                    fator_mes = Decimal('0.85')  # 15% abaixo da média no 1º semestre
                
                receita_mes = receita_mensal * fator_mes / len(propriedades)
                despesa_mes = despesa_mensal_ajustada * fator_mes / len(propriedades)
                
                # Criar receita
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_receita_vendas,
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao=f'Vendas de gado - {mes:02d}/{ano}',
                    valor=receita_mes,
                    data_competencia=data_competencia,
                    data_vencimento=data_competencia,
                    data_quitacao=data_competencia,
                    status=LancamentoFinanceiro.STATUS_QUITADO,
                )
                
                # Criar despesa
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_despesa_operacional,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    descricao=f'Despesas operacionais - {mes:02d}/{ano}',
                    valor=despesa_mes,
                    data_competencia=data_competencia,
                    data_vencimento=data_competencia,
                    data_quitacao=data_competencia,
                    status=LancamentoFinanceiro.STATUS_QUITADO,
                )
        
        print(f"[OK] Receitas e despesas criadas para {ano}")
        print(f"     Receita Anual: R$ {receita_anual:,.2f}")
        print(f"     Despesa Anual: R$ {despesa_ajustada:,.2f}")
        print(f"     Saldo Líquido: R$ {saldo_liquido_desejado:,.2f}")
    
    print()


def criar_receitas_anuais_dre(propriedades, ano_inicio, ano_fim):
    """Cria ReceitaAnual com DRE completo para cada ano"""
    print("=" * 80)
    print(f"CRIANDO RECEITAS ANUAIS E DRE - {ano_inicio} a {ano_fim}")
    print("=" * 80)
    print()
    
    receitas_base = {
        2022: Decimal('28000000.00'),
        2023: Decimal('21000000.00'),
        2024: Decimal('25200000.00'),
        2025: Decimal('29400000.00'),
    }
    
    for ano in range(ano_inicio, ano_fim + 1):
        receita_bruta_total = receitas_base.get(ano, receitas_base[2022])
        receita_por_propriedade = receita_bruta_total / len(propriedades)
        
        for propriedade in propriedades:
            # Deduções (15%)
            icms = receita_por_propriedade * Decimal('0.08')
            funrural = receita_por_propriedade * Decimal('0.05')
            outros_impostos = receita_por_propriedade * Decimal('0.02')
            
            receita_liquida = receita_por_propriedade - icms - funrural - outros_impostos
            
            # CPV (50% da receita líquida)
            cpv = receita_liquida * Decimal('0.50')
            lucro_bruto = receita_liquida - cpv
            
            # Despesas operacionais (ajustadas para saldo líquido desejado)
            saldo_liquido_desejado = SALDO_LIQUIDO_ANUAL
            if ano == 2023:
                saldo_liquido_desejado = Decimal('1200000.00')
            elif ano == 2024:
                saldo_liquido_desejado = Decimal('1500000.00')
            elif ano == 2025:
                saldo_liquido_desejado = Decimal('1900000.00')
            
            despesas_operacionais = receita_liquida - cpv - saldo_liquido_desejado
            resultado_operacional = lucro_bruto - despesas_operacionais
            
            # Despesas financeiras (5%)
            despesas_financeiras = receita_liquida * Decimal('0.05')
            lair = resultado_operacional - despesas_financeiras
            
            # Impostos (15%)
            impostos = lair * Decimal('0.15')
            lucro_liquido = lair - impostos
            
            receita_anual, created = ReceitaAnual.objects.get_or_create(
                propriedade=propriedade,
                ano=ano,
                defaults={
                    'valor_receita': receita_por_propriedade,
                    'icms_vendas': icms,
                    'funviral_vendas': funrural,
                    'outros_impostos_vendas': outros_impostos,
                    'custo_produtos_vendidos': cpv,
                    'retirada_labore': despesas_operacionais * Decimal('0.20'),
                    'depreciacao_amortizacao': despesas_operacionais * Decimal('0.10'),
                    'despesas_financeiras': despesas_financeiras,
                    'csll': impostos * Decimal('0.50'),
                    'irpj': impostos * Decimal('0.50'),
                }
            )
            
            if created:
                print(f"[OK] ReceitaAnual {ano}: {propriedade.nome_propriedade}")
                print(f"     Receita Bruta: R$ {receita_por_propriedade:,.2f}")
                print(f"     Lucro Líquido: R$ {lucro_liquido:,.2f}")
    
    print()


def main():
    """Função principal"""
    print("=" * 80)
    print("CRIAÇÃO DE DADOS HISTÓRICOS COMPLETOS - 2022 A 2025")
    print("=" * 80)
    print()
    
    # Buscar propriedades
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor Marcelo Sanguino não encontrado!")
        return
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    print(f"[OK] Propriedades encontradas: {propriedades.count()}")
    print()
    
    ano_inicio = 2022
    ano_fim = 2025
    
    # 1. Criar rebanho histórico
    inventarios = criar_rebanho_historico(propriedades, ano_inicio, ano_fim)
    
    # 2. Criar bens imobilizados
    bens = criar_bens_imobilizados(propriedades)
    
    # 3. Criar pagamentos trimestrais
    pagamentos = criar_pagamentos_trimestrais(propriedades, ano_inicio, ano_fim)
    
    # 4. Criar pagamento de avalista out/2024
    pagamento_avalista = criar_pagamento_avalista_out_2024(propriedades)
    
    # 5. Criar receitas e despesas históricas
    criar_receitas_despesas_historicas(propriedades, ano_inicio, ano_fim)
    
    # 6. Criar Receitas Anuais e DRE
    criar_receitas_anuais_dre(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] DADOS HISTÓRICOS CRIADOS COM SUCESSO!")
    print("=" * 80)
    print()
    print("Resumo:")
    print(f"  - Inventários criados: {len(inventarios)}")
    print(f"  - Bens imobilizados: {len(bens)}")
    print(f"  - Pagamentos trimestrais: {len(pagamentos)}")
    print(f"  - Pagamento avalista Out/2024: {'Sim' if pagamento_avalista else 'Não'}")
    print()
    print("Contexto histórico:")
    print("  - 2022: Ano normal")
    print("  - 2023: Queda de 25% nos preços (bezerro e gado gordo)")
    print("  - 2024: Recuperação parcial (90% do normal)")
    print("  - 2025: Acima do normal (105%)")
    print()
    print("Saldo líquido anual:")
    print("  - 2022: R$ 1,7 milhões")
    print("  - 2023: R$ 1,2 milhões (menor devido à queda)")
    print("  - 2024: R$ 1,5 milhões")
    print("  - 2025: R$ 1,9 milhões")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

