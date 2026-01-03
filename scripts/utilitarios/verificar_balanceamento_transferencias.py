# -*- coding: utf-8 -*-
"""
Script para verificar se todas as transferências estão balanceadas entre origem e destino
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from collections import defaultdict
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

print("=" * 80)
print("VERIFICAR BALANCEAMENTO DE TRANSFERENCIAS")
print("=" * 80)

# Buscar todas as transferências de saída
saidas = MovimentacaoProjetada.objects.filter(
    tipo_movimentacao='TRANSFERENCIA_SAIDA'
).select_related('propriedade', 'categoria').order_by('data_movimentacao')

# Buscar todas as transferências de entrada
entradas = MovimentacaoProjetada.objects.filter(
    tipo_movimentacao='TRANSFERENCIA_ENTRADA'
).select_related('propriedade', 'categoria').order_by('data_movimentacao')

print(f"\n[INFO] Total de saidas: {saidas.count()}")
print(f"[INFO] Total de entradas: {entradas.count()}")

# Agrupar por propriedade e categoria
problemas = []

for saida in saidas:
    # Buscar entrada correspondente (mesma data, mesma quantidade, mesma categoria)
    entrada_correspondente = entradas.filter(
        categoria=saida.categoria,
        data_movimentacao=saida.data_movimentacao,
        quantidade=saida.quantidade
    ).exclude(propriedade=saida.propriedade).first()
    
    if not entrada_correspondente:
        # Tentar encontrar por data e quantidade (pode estar em propriedade diferente)
        entrada_por_data = entradas.filter(
            categoria=saida.categoria,
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).exclude(propriedade=saida.propriedade)
        
        if not entrada_por_data.exists():
            obs_safe = saida.observacao.encode('ascii', 'ignore').decode('ascii') if saida.observacao else ''
            problemas.append({
                'tipo': 'SAIDA_SEM_ENTRADA',
                'propriedade': saida.propriedade.nome_propriedade,
                'categoria': saida.categoria.nome,
                'data': saida.data_movimentacao,
                'quantidade': saida.quantidade,
                'observacao': obs_safe[:50]
            })

# Agrupar problemas por propriedade
problemas_por_propriedade = defaultdict(list)
for prob in problemas:
    problemas_por_propriedade[prob['propriedade']].append(prob)

print(f"\n[PROBLEMAS ENCONTRADOS: {len(problemas)}]")
for propriedade, lista_problemas in problemas_por_propriedade.items():
    print(f"\n  {propriedade}: {len(lista_problemas)} transferencias sem entrada correspondente")
    for prob in lista_problemas[:5]:  # Mostrar até 5
        print(f"    - {prob['categoria']}: {prob['quantidade']} em {prob['data'].strftime('%d/%m/%Y')}")

# Verificar transferências específicas conhecidas
print(f"\n[VERIFICACAO DE TRANSFERENCIAS ESPECIFICAS]")

# Canta Galo -> Invernada Grande (Vacas Descarte)
canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

saidas_canta_descarte = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_descarte
)

entradas_invernada_descarte = MovimentacaoProjetada.objects.filter(
    propriedade=invernada,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_descarte
)

total_saidas = sum(s.quantidade for s in saidas_canta_descarte)
total_entradas = sum(e.quantidade for e in entradas_invernada_descarte)

print(f"\n  Canta Galo -> Invernada Grande (Vacas Descarte):")
print(f"    Saidas: {total_saidas}")
print(f"    Entradas: {total_entradas}")
if total_saidas == total_entradas:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas - total_entradas}")

# Canta Galo -> Favo de Mel (Garrotes)
favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

saidas_canta_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
)

entradas_favo_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
)

total_saidas_garrote = sum(s.quantidade for s in saidas_canta_garrote)
total_entradas_garrote = sum(e.quantidade for e in entradas_favo_garrote)

print(f"\n  Canta Galo -> Favo de Mel (Garrotes):")
print(f"    Saidas: {total_saidas_garrote}")
print(f"    Entradas: {total_entradas_garrote}")
if total_saidas_garrote == total_entradas_garrote:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas_garrote - total_entradas_garrote}")

# Favo de Mel -> Girassol (Garrotes)
girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')

saidas_favo_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
)

entradas_girassol_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
)

total_saidas_favo = sum(s.quantidade for s in saidas_favo_garrote)
total_entradas_girassol = sum(e.quantidade for e in entradas_girassol_garrote)

print(f"\n  Favo de Mel -> Girassol (Garrotes):")
print(f"    Saidas: {total_saidas_favo}")
print(f"    Entradas: {total_entradas_girassol}")
if total_saidas_favo == total_entradas_girassol:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas_favo - total_entradas_girassol}")

print(f"\n[OK] Verificacao concluida!")
























