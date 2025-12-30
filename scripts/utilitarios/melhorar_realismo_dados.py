#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para melhorar o realismo dos dados criados
Corrige valores por cabeça, distribuição de categorias e quantidades
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date
from random import randint, choice, uniform

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, MovimentacaoProjetada
)
from gestao_rural.models_financeiro import LancamentoFinanceiro, CategoriaFinanceira

def analisar_problemas_realismo():
    """Analisa os problemas de realismo nos dados criados"""
    print("=" * 80)
    print("ANÁLISE DE REALISMO DOS DADOS")
    print("=" * 80)
    print()
    
    problemas = []
    
    # 1. Verificar valores por cabeça
    print("1. VALORES POR CABEÇA:")
    movimentacoes = MovimentacaoProjetada.objects.filter(
        tipo_movimentacao='VENDA',
        data_movimentacao__year=2025
    )
    
    valores_por_categoria = {}
    for mov in movimentacoes:
        cat_nome = mov.categoria.nome
        if cat_nome not in valores_por_categoria:
            valores_por_categoria[cat_nome] = []
        valores_por_categoria[cat_nome].append(float(mov.valor_por_cabeca))
    
    valores_esperados = {
        'Bezerro': 2200.00,
        'Bezerra': 1500.00,
        'Garrote': 2800.00,
        'Boi': 4200.00,
    }
    
    for cat, valores in valores_por_categoria.items():
        media = sum(valores) / len(valores) if valores else 0
        print(f"   {cat}: R$ {media:,.2f} (média)")
        
        # Verificar se está próximo do esperado
        for esperado_nome, esperado_valor in valores_esperados.items():
            if esperado_nome.lower() in cat.lower():
                diff = abs(media - esperado_valor) / esperado_valor * 100
                if diff > 10:  # Mais de 10% de diferença
                    problemas.append(f"Valor de {cat} está {diff:.1f}% diferente do esperado (R$ {esperado_valor:,.2f})")
                break
    
    print()
    
    # 2. Verificar quantidades
    print("2. QUANTIDADES POR VENDA:")
    quantidades = [mov.quantidade for mov in movimentacoes]
    if quantidades:
        print(f"   Mínimo: {min(quantidades)} cabeças")
        print(f"   Máximo: {max(quantidades)} cabeças")
        print(f"   Média: {sum(quantidades)/len(quantidades):.0f} cabeças")
        
        if max(quantidades) < 200:
            problemas.append("Quantidades muito pequenas. Fazendas grandes vendem lotes de 200-500 cabeças")
    
    print()
    
    # 3. Verificar distribuição mensal
    print("3. DISTRIBUIÇÃO MENSAL:")
    vendas_por_mes = {}
    for mov in movimentacoes:
        mes = mov.data_movimentacao.month
        vendas_por_mes[mes] = vendas_por_mes.get(mes, 0) + mov.quantidade
    
    for mes in sorted(vendas_por_mes.keys()):
        print(f"   {mes:02d}/2025: {vendas_por_mes[mes]} cabeças")
    
    # Verificar se primeiro semestre tem poucas vendas
    primeiro_semestre = sum(vendas_por_mes.get(m, 0) for m in range(1, 7))
    segundo_semestre = sum(vendas_por_mes.get(m, 0) for m in range(7, 13))
    total = primeiro_semestre + segundo_semestre
    
    if total > 0:
        perc_1sem = primeiro_semestre / total * 100
        perc_2sem = segundo_semestre / total * 100
        print(f"   1º Semestre: {perc_1sem:.1f}%")
        print(f"   2º Semestre: {perc_2sem:.1f}%")
        
        if perc_1sem > 30:
            problemas.append("Primeiro semestre tem muitas vendas. Normalmente concentra no 2º semestre")
    
    print()
    
    # 4. Verificar categorias vendidas
    print("4. CATEGORIAS VENDIDAS:")
    categorias_vendidas = {}
    for mov in movimentacoes:
        cat = mov.categoria.nome
        categorias_vendidas[cat] = categorias_vendidas.get(cat, 0) + mov.quantidade
    
    for cat, qtd in sorted(categorias_vendidas.items(), key=lambda x: x[1], reverse=True):
        perc = qtd / sum(categorias_vendidas.values()) * 100
        print(f"   {cat}: {qtd} cabeças ({perc:.1f}%)")
        
        # Bezerros não deveriam ser maioria
        if 'bezerro' in cat.lower() and perc > 40:
            problemas.append(f"Muitos bezerros sendo vendidos ({perc:.1f}%). Normalmente vendem mais boi gordo")
    
    print()
    
    # 5. Resumo de problemas
    if problemas:
        print("=" * 80)
        print("PROBLEMAS IDENTIFICADOS:")
        print("=" * 80)
        for i, problema in enumerate(problemas, 1):
            print(f"{i}. {problema}")
        print()
    else:
        print("✅ Nenhum problema crítico identificado!")
        print()
    
    return problemas


def melhorar_dados():
    """Melhora o realismo dos dados existentes"""
    print("=" * 80)
    print("MELHORANDO REALISMO DOS DADOS")
    print("=" * 80)
    print()
    
    # Valores realistas por categoria
    valores_por_categoria = {
        'Bezerro': Decimal('2200.00'),
        'Bezerra': Decimal('1500.00'),
        'Garrote': Decimal('2800.00'),
        'Novilho': Decimal('3200.00'),
        'Boi': Decimal('4200.00'),
        'Boi Gordo': Decimal('4200.00'),
    }
    
    # Buscar movimentações de venda
    movimentacoes = MovimentacaoProjetada.objects.filter(
        tipo_movimentacao='VENDA',
        data_movimentacao__year=2025
    )
    
    print(f"Movimentações encontradas: {movimentacoes.count()}")
    print()
    
    atualizadas = 0
    for mov in movimentacoes:
        cat_nome = mov.categoria.nome
        
        # Determinar valor correto baseado na categoria
        valor_correto = None
        for cat_key, valor in valores_por_categoria.items():
            if cat_key.lower() in cat_nome.lower():
                valor_correto = valor
                break
        
        if not valor_correto:
            # Se não encontrou, usar valor padrão baseado no tipo
            if 'bezerro' in cat_nome.lower() and 'bezerra' not in cat_nome.lower():
                valor_correto = Decimal('2200.00')
            elif 'bezerra' in cat_nome.lower():
                valor_correto = Decimal('1500.00')
            elif 'garrote' in cat_nome.lower():
                valor_correto = Decimal('2800.00')
            elif 'boi' in cat_nome.lower():
                valor_correto = Decimal('4200.00')
            else:
                valor_correto = Decimal('3000.00')  # Valor médio
        
        # Atualizar se necessário
        if mov.valor_por_cabeca != valor_correto:
            mov.valor_por_cabeca = valor_correto
            mov.valor_total = valor_correto * Decimal(str(mov.quantidade))
            mov.save()
            atualizadas += 1
            print(f"[OK] Atualizado: {mov.propriedade.nome_propriedade} - {mov.quantidade} {cat_nome} - R$ {valor_correto:,.2f}/cabeça")
    
    print()
    print(f"Total de movimentações atualizadas: {atualizadas}")
    print()


if __name__ == '__main__':
    try:
        # 1. Analisar problemas
        problemas = analisar_problemas_realismo()
        
        # 2. Melhorar dados
        if problemas:
            resposta = input("Deseja corrigir os problemas identificados? (s/n): ")
            if resposta.lower() == 's':
                melhorar_dados()
                print("=" * 80)
                print("✅ DADOS MELHORADOS!")
                print("=" * 80)
        else:
            print("✅ Dados já estão realistas!")
        
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

