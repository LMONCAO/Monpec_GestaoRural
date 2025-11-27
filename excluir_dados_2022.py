# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models_financeiro import LancamentoFinanceiro
from gestao_rural.models_compras_financeiro import NotaFiscal

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("EXCLUINDO DADOS FINANCEIROS DE 2022")
print("=" * 70)

# Contar antes de excluir
lancamentos = LancamentoFinanceiro.objects.filter(data_competencia__year=2022)
notas = NotaFiscal.objects.filter(data_emissao__year=2022)

total_lancamentos = lancamentos.count()
total_notas = notas.count()

print(f"\nEncontrados:")
print(f"  - {total_lancamentos:,} lancamentos financeiros")
print(f"  - {total_notas:,} notas fiscais")

if total_lancamentos == 0 and total_notas == 0:
    print("\n[OK] Nenhum dado de 2022 para excluir.")
    sys.exit(0)

# Confirmar (pode ser pulado com --yes)
if '--yes' not in sys.argv:
    print(f"\nTem certeza que deseja excluir todos esses dados? (s/n): ", end='')
    resposta = input().strip().lower()
    
    if resposta != 's':
        print("\nOperacao cancelada.")
        sys.exit(0)

# Excluir
print("\nExcluindo...")
lancamentos.delete()
notas.delete()

print(f"\n[OK] {total_lancamentos:,} lancamentos excluidos")
print(f"[OK] {total_notas:,} notas fiscais excluidas")
print("\n" + "=" * 70)
print("DADOS EXCLUIDOS COM SUCESSO!")
print("=" * 70)
print("\nAgora voce pode regenerar os dados com valores mais realistas usando:")
print("  python manage.py carregar_dados_financeiro_realista --ano 2022 --receita-media 200000 --despesa-media 180000")

