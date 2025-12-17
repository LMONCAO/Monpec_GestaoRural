# -*- coding: utf-8 -*-
"""
Script para verificação completa e sincronizada de todas as fazendas
Garante que saldos batem matematicamente e logicamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
)
from datetime import date
from collections import defaultdict

print("=" * 80)
print("VERIFICACAO COMPLETA E SINCRONIZADA - TODAS AS FAZENDAS")
print("=" * 80)

# Buscar todas as fazendas
fazendas = Propriedade.objects.all().order_by('nome_propriedade')
print(f"\n[INFO] Fazendas encontradas: {fazendas.count()}")

# Anos a verificar
anos = [2022, 2023, 2024, 2025, 2026]

# Armazenar problemas encontrados
problemas = []

# 1. VERIFICAR SALDOS NEGATIVOS POR FAZENDA E CATEGORIA
print("\n" + "=" * 80)
print("1. VERIFICAR SALDOS NEGATIVOS")
print("=" * 80)

for fazenda in fazendas:
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=fazenda
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        continue
    
    print(f"\n[{fazenda.nome_propriedade}]")
    
    for ano in anos:
        # Buscar todas as categorias com movimentações neste ano
        categorias = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            data_movimentacao__year=ano,
            planejamento=planejamento
        ).values_list('categoria', flat=True).distinct()
        
        for categoria_id in categorias:
            categoria = CategoriaAnimal.objects.get(id=categoria_id)
            
            # Calcular saldo inicial
            inventario = InventarioRebanho.objects.filter(
                propriedade=fazenda,
                categoria=categoria,
                data_inventario__lte=date(ano, 12, 31)
            ).order_by('-data_inventario').first()
            
            saldo = inventario.quantidade if inventario else 0
            
            # Se não há inventário para este ano, usar saldo final do ano anterior
            if not inventario or inventario.data_inventario.year < ano:
                if ano > 2022:
                    # Calcular saldo final do ano anterior
                    inventario_anterior = InventarioRebanho.objects.filter(
                        propriedade=fazenda,
                        categoria=categoria,
                        data_inventario__lte=date(ano - 1, 12, 31)
                    ).order_by('-data_inventario').first()
                    
                    saldo = inventario_anterior.quantidade if inventario_anterior else 0
                    
                    # Adicionar movimentações do ano anterior
                    movimentacoes_anterior = MovimentacaoProjetada.objects.filter(
                        propriedade=fazenda,
                        categoria=categoria,
                        data_movimentacao__year=ano - 1,
                        planejamento=planejamento
                    ).order_by('data_movimentacao')
                    
                    for mov in movimentacoes_anterior:
                        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
                            saldo += mov.quantidade
                        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                            saldo -= mov.quantidade
            
            # Processar movimentações do ano
            movimentacoes = MovimentacaoProjetada.objects.filter(
                propriedade=fazenda,
                categoria=categoria,
                data_movimentacao__year=ano,
                planejamento=planejamento
            ).order_by('data_movimentacao')
            
            saldo_minimo = saldo
            movimentacao_problema = None
            
            for mov in movimentacoes:
                if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
                    saldo += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                    if saldo < mov.quantidade:
                        if not movimentacao_problema:
                            movimentacao_problema = mov
                        saldo_minimo = min(saldo_minimo, saldo - mov.quantidade)
                    saldo -= mov.quantidade
            
            if saldo_minimo < 0:
                problemas.append({
                    'tipo': 'SALDO_NEGATIVO',
                    'fazenda': fazenda.nome_propriedade,
                    'ano': ano,
                    'categoria': categoria.nome,
                    'saldo_minimo': saldo_minimo,
                    'movimentacao': movimentacao_problema
                })
                print(f"  [ERRO] {ano} - {categoria.nome}: Saldo minimo = {saldo_minimo}")

# 2. VERIFICAR TRANSFERENCIAS DESBALANCEADAS
print("\n" + "=" * 80)
print("2. VERIFICAR TRANSFERENCIAS DESBALANCEADAS")
print("=" * 80)

transferencias_por_data = defaultdict(lambda: {'saidas': [], 'entradas': []})

for fazenda in fazendas:
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=fazenda
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        continue
    
    # Buscar todas as transferências de saída
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento
    )
    
    for saida in saidas:
        key = (saida.data_movimentacao, saida.categoria.id, saida.observacao or '')
        transferencias_por_data[key]['saidas'].append({
            'fazenda': fazenda.nome_propriedade,
            'quantidade': saida.quantidade,
            'movimentacao': saida
        })
    
    # Buscar todas as transferências de entrada
    entradas = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento
    )
    
    for entrada in entradas:
        key = (entrada.data_movimentacao, entrada.categoria.id, entrada.observacao or '')
        transferencias_por_data[key]['entradas'].append({
            'fazenda': fazenda.nome_propriedade,
            'quantidade': entrada.quantidade,
            'movimentacao': entrada
        })

for key, dados in transferencias_por_data.items():
    data_transf, categoria_id, obs = key
    categoria = CategoriaAnimal.objects.get(id=categoria_id)
    
    total_saidas = sum(s['quantidade'] for s in dados['saidas'])
    total_entradas = sum(e['quantidade'] for e in dados['entradas'])
    
    if total_saidas != total_entradas:
        problemas.append({
            'tipo': 'TRANSFERENCIA_DESBALANCEADA',
            'data': data_transf,
            'categoria': categoria.nome,
            'total_saidas': total_saidas,
            'total_entradas': total_entradas,
            'saidas': dados['saidas'],
            'entradas': dados['entradas']
        })
        print(f"  [ERRO] {data_transf.strftime('%d/%m/%Y')} - {categoria.nome}:")
        print(f"    Saidas: {total_saidas} (fazendas: {[s['fazenda'] for s in dados['saidas']]})")
        print(f"    Entradas: {total_entradas} (fazendas: {[e['fazenda'] for e in dados['entradas']]})")

# 3. VERIFICAR PROMOCOES ANTES DE SAIDAS
print("\n" + "=" * 80)
print("3. VERIFICAR PROMOCOES ANTES DE SAIDAS")
print("=" * 80)

for fazenda in fazendas:
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=fazenda
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        continue
    
    # Buscar todas as saídas (vendas, transferências, mortes)
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        tipo_movimentacao__in=['VENDA', 'TRANSFERENCIA_SAIDA', 'MORTE'],
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    for saida in saidas:
        # Verificar se há promoção de entrada antes desta saída
        promocoes_antes = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            categoria=saida.categoria,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            data_movimentacao__lte=saida.data_movimentacao,
            data_movimentacao__year=saida.data_movimentacao.year,
            planejamento=planejamento
        )
        
        total_promocoes = sum(p.quantidade for p in promocoes_antes)
        
        # Calcular saldo disponível
        inventario = InventarioRebanho.objects.filter(
            propriedade=fazenda,
            categoria=saida.categoria,
            data_inventario__lte=saida.data_movimentacao
        ).order_by('-data_inventario').first()
        
        saldo = inventario.quantidade if inventario else 0
        
        # Adicionar todas as movimentações anteriores
        movimentacoes_anteriores = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            categoria=saida.categoria,
            data_movimentacao__lt=saida.data_movimentacao,
            planejamento=planejamento
        )
        
        for mov in movimentacoes_anteriores:
            if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
                saldo += mov.quantidade
            elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                saldo -= mov.quantidade
        
        # Adicionar promoções do mesmo ano
        saldo += total_promocoes
        
        # Subtrair outras saídas do mesmo ano antes desta
        outras_saidas = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            categoria=saida.categoria,
            tipo_movimentacao__in=['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA'],
            data_movimentacao__lt=saida.data_movimentacao,
            data_movimentacao__year=saida.data_movimentacao.year,
            planejamento=planejamento
        )
        
        total_outras_saidas = sum(s.quantidade for s in outras_saidas)
        saldo -= total_outras_saidas
        
        if saldo < saida.quantidade:
            problemas.append({
                'tipo': 'SAIDA_SEM_SALDO',
                'fazenda': fazenda.nome_propriedade,
                'data': saida.data_movimentacao,
                'categoria': saida.categoria.nome,
                'quantidade': saida.quantidade,
                'saldo_disponivel': saldo,
                'movimentacao': saida
            })
            print(f"  [ERRO] {fazenda.nome_propriedade} - {saida.data_movimentacao.strftime('%d/%m/%Y')} - {saida.categoria.nome}:")
            print(f"    Saida: {saida.quantidade}, Saldo disponivel: {saldo}")

# RESUMO FINAL
print("\n" + "=" * 80)
print("RESUMO DE PROBLEMAS ENCONTRADOS")
print("=" * 80)

print(f"\nTotal de problemas: {len(problemas)}")

por_tipo = defaultdict(int)
for problema in problemas:
    por_tipo[problema['tipo']] += 1

for tipo, count in por_tipo.items():
    print(f"  {tipo}: {count}")

if problemas:
    print(f"\n[AVISO] Foram encontrados {len(problemas)} problemas que precisam ser corrigidos")
    print(f"[INFO] Execute o script de correcao para resolver os problemas")
else:
    print(f"\n[OK] Nenhum problema encontrado! Todas as fazendas estao sincronizadas.")

print(f"\n[OK] Verificacao concluida!")

