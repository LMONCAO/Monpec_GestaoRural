#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Criar pagamentos corretos de 2025
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import LancamentoFinanceiro, CategoriaFinanceira

categoria_pagamento_financiamento, _ = CategoriaFinanceira.objects.get_or_create(
    nome='Pagamento de Financiamento',
    tipo=CategoriaFinanceira.TIPO_DESPESA
)

canta_galo = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo').first()

# Deletar pagamentos existentes de 2025
LancamentoFinanceiro.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_pagamento_financiamento,
    data_competencia__year=2025
).delete()

# Criar apenas os 3 pagamentos corretos
PAGAMENTO_TRIMESTRAL = Decimal('1500000.00')
meses_corretos = [1, 4, 7]

for mes in meses_corretos:
    data_pagamento = date(2025, mes, 15)
    LancamentoFinanceiro.objects.create(
        propriedade=canta_galo,
        categoria=categoria_pagamento_financiamento,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        descricao=f'Pagamento trimestral de financiamento - {mes}/2025',
        valor=PAGAMENTO_TRIMESTRAL,
        data_competencia=data_pagamento,
        data_vencimento=data_pagamento,
        data_quitacao=data_pagamento,
        status=LancamentoFinanceiro.STATUS_QUITADO,
    )
    print(f"[OK] Pagamento criado: {mes:02d}/2025 - R$ {PAGAMENTO_TRIMESTRAL:,.2f}")

print()
print("Pagamentos de 2025 criados corretamente!")

