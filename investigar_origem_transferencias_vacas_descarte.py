# -*- coding: utf-8 -*-
"""
Script para investigar a origem das transferências de Vacas Descarte
Verifica se são criadas automaticamente ou manualmente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, ConfiguracaoVenda
)
from datetime import date

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

planejamento_atual = PlanejamentoAnual.objects.filter(
    propriedade=canta_galo
).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("INVESTIGAR ORIGEM TRANSFERENCIAS VACAS DESCARTE")
print("=" * 80)

print(f"\n[INFO] Planejamento atual: {planejamento_atual.codigo}")

# Buscar TODAS as transferências de Vacas Descarte
transferencias = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    planejamento=planejamento_atual
).order_by('data_movimentacao')

print(f"\n[TRANSFERENCIAS ENCONTRADAS]")
print(f"Total: {transferencias.count()}")

for t in transferencias:
    print(f"\n  Data: {t.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"  Quantidade: {t.quantidade}")
    print(f"  Observacao: {t.observacao}")
    print(f"  Data criacao: {t.data_criacao if hasattr(t, 'data_criacao') else 'N/A'}")
    print(f"  ID: {t.id}")

# Verificar se há configurações de venda/transferência automática
print(f"\n[CONFIGURACOES DE TRANSFERENCIA]")
configuracoes = ConfiguracaoVenda.objects.filter(
    propriedade_origem=canta_galo,
    categoria=categoria_descarte
)

print(f"Total: {configuracoes.count()}")

for config in configuracoes:
    print(f"\n  Propriedade destino: {config.propriedade_destino.nome_propriedade if config.propriedade_destino else 'N/A'}")
    print(f"  Categoria: {config.categoria.nome}")
    print(f"  Tipo: {config.tipo_configuracao}")
    print(f"  Ativo: {config.ativo if hasattr(config, 'ativo') else 'N/A'}")

# Verificar transferências por ano
print(f"\n[TRANSFERENCIAS POR ANO]")
anos = [2022, 2023, 2024, 2025, 2026]

for ano in anos:
    transferencias_ano = transferencias.filter(data_movimentacao__year=ano)
    if transferencias_ano.exists():
        print(f"\n  {ano}:")
        for t in transferencias_ano:
            print(f"    {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} vacas")
            print(f"      Observacao: {t.observacao}")

# Verificar se há alguma lógica automática criando essas transferências
print(f"\n[VERIFICAR LOGICA AUTOMATICA]")
print(f"Verificando se ha alguma configuracao que cria transferencias automaticamente...")

# Buscar todas as movimentações relacionadas
print(f"\n[TODAS MOVIMENTACOES VACAS DESCARTE]")
todas_movimentacoes = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte,
    planejamento=planejamento_atual
).order_by('data_movimentacao', 'tipo_movimentacao')

for mov in todas_movimentacoes:
    print(f"  {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.tipo_movimentacao} - {mov.quantidade} - {mov.observacao}")

print(f"\n[OK] Investigacao concluida!")
























