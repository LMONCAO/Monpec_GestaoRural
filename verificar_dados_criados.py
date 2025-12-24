#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar os dados criados"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, InventarioRebanho, BemImobilizado,
    SCRBancoCentral
)
from gestao_rural.models_financeiro import LancamentoFinanceiro, ReceitaAnual
from decimal import Decimal

produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
if not produtor:
    print("Produtor não encontrado!")
    sys.exit(1)

propriedades = Propriedade.objects.filter(produtor=produtor)
canta_galo = propriedades.filter(nome_propriedade__icontains='Canta Galo').first()

print("=" * 80)
print("VERIFICAÇÃO DOS DADOS CRIADOS")
print("=" * 80)
print()

if canta_galo:
    print(f"Propriedade: {canta_galo.nome_propriedade}")
    print()
    
    # Inventários
    inventarios = InventarioRebanho.objects.filter(propriedade=canta_galo)
    print(f"Inventários: {inventarios.count()}")
    total_rebanho = sum(inv.valor_total for inv in inventarios)
    print(f"Valor total do rebanho: R$ {total_rebanho:,.2f}")
    print()
    
    # Bens
    bens = BemImobilizado.objects.filter(propriedade=canta_galo, ativo=True)
    print(f"Bens imobilizados: {bens.count()}")
    total_bens = sum(bem.valor_aquisicao for bem in bens)
    print(f"Valor total dos bens: R$ {total_bens:,.2f}")
    print()
    
    # Lançamentos
    lancamentos = LancamentoFinanceiro.objects.filter(propriedade=canta_galo)
    print(f"Lançamentos financeiros: {lancamentos.count()}")
    
    receitas = lancamentos.filter(tipo='RECEITA')
    despesas = lancamentos.filter(tipo='DESPESA')
    
    total_receitas = sum(l.valor for l in receitas)
    total_despesas = sum(l.valor for l in despesas)
    
    print(f"  Receitas: {receitas.count()} - Total: R$ {total_receitas:,.2f}")
    print(f"  Despesas: {despesas.count()} - Total: R$ {total_despesas:,.2f}")
    print(f"  Saldo: R$ {total_receitas - total_despesas:,.2f}")
    print()
    
    # Receitas Anuais
    receitas_anuais = ReceitaAnual.objects.filter(propriedade=canta_galo)
    print(f"Receitas Anuais: {receitas_anuais.count()}")
    for ra in receitas_anuais:
        print(f"  {ra.ano}: R$ {ra.valor_receita:,.2f}")
    print()
    
    # SCR
    scrs = SCRBancoCentral.objects.filter(produtor=produtor)
    print(f"SCRs: {scrs.count()}")
    for scr in scrs:
        print(f"  {scr.data_referencia_scr}: {scr.dividas.count()} bancos")
        total_dividas = sum(d.valor_total for d in scr.dividas.all())
        print(f"    Total dívidas: R$ {total_dividas:,.2f}")
    print()

# Todas as propriedades
print("=" * 80)
print("TODAS AS PROPRIEDADES")
print("=" * 80)
for prop in propriedades:
    inventarios = InventarioRebanho.objects.filter(propriedade=prop)
    receitas_anuais = ReceitaAnual.objects.filter(propriedade=prop)
    lancamentos = LancamentoFinanceiro.objects.filter(propriedade=prop)
    
    print(f"{prop.nome_propriedade}:")
    print(f"  Inventários: {inventarios.count()}")
    print(f"  Receitas Anuais: {receitas_anuais.count()}")
    print(f"  Lançamentos: {lancamentos.count()}")
    print()

