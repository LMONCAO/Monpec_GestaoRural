#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar dívidas SCR do Marcelo Sanguino baseado no PDF fornecido
Dados extraídos do SCR-86165550134-202511-26112025-184636735-97038546.pdf
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, SCRBancoCentral, DividaBanco, ContratoDivida
)

# Dados extraídos do SCR (Outubro/2025)
DADOS_SCR = {
    'data_referencia': date(2025, 10, 31),
    'cpf_cnpj': '861.655.501-34',
    'nome': 'MARCELO SANGUINO',
    'dividas_por_banco': [
        {
            'banco': 'BANCO COOPERATIVO SICREDI S.A.',
            'em_dia': Decimal('827401.12'),
            'vencida': Decimal('0.00'),
            'tipo': 'Outros financiamentos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO, POUPANÇA E INVESTIMENTO CELEIRO CENTRO OESTE - SICREDI CELEIRO CENTRO OESTE',
            'em_dia': Decimal('816806.35'),
            'vencida': Decimal('56048.42'),
            'tipo': 'Financiamentos rurais - Investimento',
        },
        {
            'banco': 'BANCO SANTANDER (BRASIL) S.A.',
            'em_dia': Decimal('738.21'),
            'vencida': Decimal('2599.54'),
            'tipo': 'Empréstimos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO, POUPANÇA E INVESTIMENTO DE CAMPO GRANDE E REGIÃO - SICREDI CAMPO GRANDE MS',
            'em_dia': Decimal('1853757.54'),
            'vencida': Decimal('2937442.06'),
            'tipo': 'Empréstimos e Financiamentos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO, POUPANÇA E INVESTIMENTO DO ARAGUAIA E XINGU - SICREDI ARAXINGU',
            'em_dia': Decimal('5260087.28'),
            'vencida': Decimal('2334980.55'),
            'tipo': 'Empréstimos e Financiamentos',
        },
        {
            'banco': 'CAIXA ECONOMICA FEDERAL',
            'em_dia': Decimal('1331149.24'),
            'vencida': Decimal('95256.36'),
            'tipo': 'Empréstimos e Financiamentos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO DOS MÉDICOS, PROFISSIONAIS DA SAÚDE E EMPRESÁRIOS DE MATO GROSSO',
            'em_dia': Decimal('424186.65'),
            'vencida': Decimal('296715.72'),
            'tipo': 'Empréstimos',
        },
        {
            'banco': 'BANCO COOPERATIVO SICOOB S.A. - BANCO SICOOB',
            'em_dia': Decimal('135514.64'),
            'vencida': Decimal('30393.90'),
            'tipo': 'Empréstimos e Financiamentos',
        },
        {
            'banco': 'CREDISIS PRIMACREDI COOPERATIVA DE CRÉDITO',
            'em_dia': Decimal('0.00'),
            'vencida': Decimal('23766.71'),
            'tipo': 'Empréstimos',
        },
        {
            'banco': 'COOPERATIVA DE CREDITO CREDICITRUS',
            'em_dia': Decimal('2605672.62'),
            'vencida': Decimal('2127595.74'),
            'tipo': 'Empréstimos e Financiamentos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO DE LIVRE ADMISSÃO DE RIO VERDE E REGIÃO LTDA.',
            'em_dia': Decimal('1831104.16'),
            'vencida': Decimal('0.00'),
            'tipo': 'Empréstimos',
        },
        {
            'banco': 'COOPERATIVA DE CRÉDITO SICOOB CREDSEGURO LTDA.',
            'em_dia': Decimal('0.00'),
            'vencida': Decimal('10038.56'),
            'tipo': 'Empréstimos',
        },
        {
            'banco': 'BANCO TOYOTA DO BRASIL S.A.',
            'em_dia': Decimal('228110.09'),
            'vencida': Decimal('0.00'),
            'tipo': 'Financiamentos',
        },
    ],
    'coobrigacoes': Decimal('823103.47'),
    'limites_credito': Decimal('34912.39'),
}

# Totais do SCR
TOTAL_EM_DIA = Decimal('14497721.55')
TOTAL_VENCIDA = Decimal('8639129.63')


def criar_scr_marcelo_sanguino():
    """Cria registro SCR do Marcelo Sanguino"""
    print("=" * 80)
    print("CRIANDO DADOS DO SCR - MARCELO SANGUINO")
    print("=" * 80)
    print()
    
    # Buscar produtor
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor Marcelo Sanguino não encontrado!")
        return None
    
    # Criar SCR
    scr, created = SCRBancoCentral.objects.get_or_create(
        produtor=produtor,
        data_referencia_scr=DADOS_SCR['data_referencia'],
        defaults={
            'status': 'IMPORTADO',
            'observacoes': f'SCR importado - Total em dia: R$ {TOTAL_EM_DIA:,.2f}, Total vencida: R$ {TOTAL_VENCIDA:,.2f}',
        }
    )
    
    if created:
        print(f"[OK] SCR criado: {scr.data_referencia_scr}")
    else:
        print(f"[OK] SCR já existe: {scr.data_referencia_scr}")
    
    print()
    
    # Criar dívidas por banco
    dividas_criadas = []
    for divida_data in DADOS_SCR['dividas_por_banco']:
        valor_total = divida_data['em_dia'] + divida_data['vencida']
        
        if valor_total > 0:
            divida, created = DividaBanco.objects.get_or_create(
                scr=scr,
                banco=divida_data['banco'],
                defaults={
                    'status_divida': 'VENCIDO' if divida_data['vencida'] > 0 else 'A_VENCER',
                    'valor_total': valor_total,
                    'quantidade_contratos': 1,
                }
            )
            
            if created:
                dividas_criadas.append(divida)
                print(f"[OK] Dívida criada: {divida.banco}")
                print(f"     Em dia: R$ {divida_data['em_dia']:,.2f}")
                print(f"     Vencida: R$ {divida_data['vencida']:,.2f}")
                print(f"     Total: R$ {valor_total:,.2f}")
    
    print()
    print(f"Total de dívidas criadas: {len(dividas_criadas)}")
    print(f"Total em dia: R$ {TOTAL_EM_DIA:,.2f}")
    print(f"Total vencida: R$ {TOTAL_VENCIDA:,.2f}")
    print(f"Total geral: R$ {TOTAL_EM_DIA + TOTAL_VENCIDA:,.2f}")
    print()
    
    return scr


if __name__ == '__main__':
    try:
        scr = criar_scr_marcelo_sanguino()
        sys.exit(0 if scr else 1)
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

