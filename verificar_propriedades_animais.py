# -*- coding: utf-8 -*-
"""Script temporário para verificar propriedades com animais ativos"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, AnimalIndividual

print("\n" + "="*60)
print("PROPRIEDADES COM ANIMAIS ATIVOS")
print("="*60 + "\n")

propriedades_com_animais = []
for p in Propriedade.objects.all():
    total_ativos = AnimalIndividual.objects.filter(propriedade=p, status='ATIVO').count()
    if total_ativos > 0:
        propriedades_com_animais.append((p.id, p.nome_propriedade, total_ativos))
        print(f"ID: {p.id:3d} | {p.nome_propriedade:40s} | {total_ativos:4d} animais ativos")

if not propriedades_com_animais:
    print("\n[AVISO] Nenhuma propriedade encontrada com animais ativos!")
    print("        Cadastre alguns animais antes de gerar o PDF de teste.")
else:
    print(f"\n[INFO] Total de propriedades com animais: {len(propriedades_com_animais)}")
    print(f"\n[SUGESTAO] Use o ID de uma das propriedades acima para gerar o PDF:")
    print(f"          python gerar_pdf_teste_realista_bnd_sisbov.py {propriedades_com_animais[0][0]}")

print("\n" + "="*60 + "\n")


