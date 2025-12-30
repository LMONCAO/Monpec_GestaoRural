# -*- coding: utf-8 -*-
"""
Script para verificar estado final de Vacas Descarte em TODOS os planejamentos
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR ESTADO FINAL - TODOS OS PLANEJAMENTOS")
print("=" * 80)

planejamentos = PlanejamentoAnual.objects.filter(
    propriedade=canta_galo
).order_by('-data_criacao', '-ano')

print(f"\n[INFO] Total de planejamentos: {planejamentos.count()}")

for planejamento in planejamentos:
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento
    )
    
    if transferencias.exists():
        print(f"\n[PLANEJAMENTO] {planejamento.codigo} - {transferencias.count()} transferencias")
        for t in transferencias:
            print(f"  {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} vacas")

print(f"\n[OK] Verificacao concluida!")
























