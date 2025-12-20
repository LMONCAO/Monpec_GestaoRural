# -*- coding: utf-8 -*-
"""
Script para verificar se as transferências do Favo de Mel estão vinculadas ao planejamento correto
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual

favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print("=" * 60)
print("VERIFICAR VINCULACAO TRANSFERENCIAS FAVO DE MEL")
print("=" * 60)

# Buscar planejamentos
planejamentos = PlanejamentoAnual.objects.filter(propriedade=favo_mel).order_by('-ano', '-data_criacao')
print(f"\n[INFO] Planejamentos encontrados:")
for p in planejamentos[:5]:
    print(f"   - {p.codigo} (ano {p.ano}, criado em {p.data_criacao.strftime('%d/%m/%Y')})")

planejamento_atual = planejamentos.first()
if planejamento_atual:
    print(f"\n[INFO] Planejamento atual: {planejamento_atual.codigo} (ano {planejamento_atual.ano})")

# Verificar transferências de entrada
print(f"\n[INFO] Transferencias de ENTRADA no Favo de Mel:")
entradas = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria
).order_by('data_movimentacao')

for e in entradas:
    planejamento_info = f"Planejamento: {e.planejamento.codigo if e.planejamento else 'SEM PLANEJAMENTO'}"
    print(f"   + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} - {planejamento_info}")

# Verificar transferências sem planejamento
entradas_sem_planejamento = entradas.filter(planejamento__isnull=True)
if entradas_sem_planejamento.exists():
    print(f"\n[ERRO] {entradas_sem_planejamento.count()} transferencias SEM PLANEJAMENTO!")
    print("   Vinculando ao planejamento atual...")
    entradas_sem_planejamento.update(planejamento=planejamento_atual)
    print("   [OK] Transferencias vinculadas")

# Verificar transferências de saída
print(f"\n[INFO] Transferencias de SAIDA do Favo de Mel:")
saidas = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria
).order_by('data_movimentacao')

for s in saidas:
    planejamento_info = f"Planejamento: {s.planejamento.codigo if s.planejamento else 'SEM PLANEJAMENTO'}"
    print(f"   - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade} - {planejamento_info}")

# Verificar transferências de saída sem planejamento
saidas_sem_planejamento = saidas.filter(planejamento__isnull=True)
if saidas_sem_planejamento.exists():
    print(f"\n[ERRO] {saidas_sem_planejamento.count()} transferencias de saida SEM PLANEJAMENTO!")
    print("   Vinculando ao planejamento atual...")
    saidas_sem_planejamento.update(planejamento=planejamento_atual)
    print("   [OK] Transferencias vinculadas")

print(f"\n[OK] Verificacao concluida!")
























