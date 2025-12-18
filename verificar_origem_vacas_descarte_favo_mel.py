# -*- coding: utf-8 -*-
"""
Script para verificar de onde estão vindo as 1.024 vacas descarte no Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 60)
print("VERIFICAR ORIGEM VACAS DESCARTE - FAVO DE MEL")
print("=" * 60)

# Buscar transferências de entrada de vacas descarte
transferencias_entrada = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_descarte
).order_by('data_movimentacao')

print(f"\n[INFO] Transferencias de ENTRADA de Vacas Descarte no Favo de Mel: {transferencias_entrada.count()}")

for t in transferencias_entrada:
    print(f"\n   Data: {t.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"   Quantidade: {t.quantidade}")
    print(f"   Observacao: {t.observacao or 'Sem observacao'}")
    print(f"   Planejamento: {t.planejamento.codigo if t.planejamento else 'Sem planejamento'}")

# Buscar transferências de saída correspondentes (de outras propriedades)
print(f"\n[INFO] Verificando transferencias de SAIDA de outras propriedades...")

# Buscar todas as propriedades
propriedades = Propriedade.objects.all()

for prop in propriedades:
    if prop == favo_mel:
        continue
    
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=prop,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        observacao__icontains='Favo de Mel'
    ).order_by('data_movimentacao')
    
    if transferencias_saida.exists():
        print(f"\n   Propriedade: {prop.nome_propriedade}")
        for t in transferencias_saida:
            print(f"      - {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} (obs: {t.observacao or 'Sem obs'})")

# Verificar se há transferências sem observação que possam estar relacionadas
print(f"\n[INFO] Verificando todas as transferencias de SAIDA de Vacas Descarte...")
todas_saidas = MovimentacaoProjetada.objects.filter(
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_descarte,
    data_movimentacao__year__in=[2022, 2023, 2024]
).order_by('data_movimentacao', 'propriedade')

for t in todas_saidas:
    print(f"   {t.propriedade.nome_propriedade} -> {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} (obs: {t.observacao or 'Sem obs'})")

print(f"\n[OK] Verificacao concluida!")




















