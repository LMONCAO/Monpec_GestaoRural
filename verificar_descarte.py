# -*- coding: utf-8 -*-
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import MovimentacaoProjetada, Propriedade

canta_galo = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo').first()
if canta_galo:
    descarte = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo, 
        tipo_movimentacao='TRANSFERENCIA_SAIDA', 
        data_movimentacao__year__gte=2024, 
        categoria__nome__icontains='Descarte'
    ).select_related('categoria')
    
    print(f'Transferencias de descarte (2024+): {descarte.count()}')
    for d in descarte:
        print(f'  - {d.data_movimentacao.strftime("%d/%m/%Y")}: {d.quantidade} {d.categoria.nome} - {d.observacao[:50]}')





















