#!/usr/bin/env python
"""
Script para popular projetos bancários da Fazenda Demonstração
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models import ProjetoBancario, TipoFinanciamento, Financiamento

def main():
    print("="*60)
    print("POPULANDO PROJETOS BANCARIOS - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar tipos de financiamento
    tipos_fin_data = [
        {'nome': 'Pronaf - Custeio', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Custeio'},
        {'nome': 'Pronaf - Investimento', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Investimento'},
        {'nome': 'FCO - Custeio', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Custeio'},
        {'nome': 'FCO - Investimento', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Investimento'},
        {'nome': 'Credito Rural Privado', 'descricao': 'Credito rural oferecido por bancos privados'},
    ]

    tipos_fin = []
    for tipo_data in tipos_fin_data:
        tipo, created = TipoFinanciamento.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={'descricao': tipo_data['descricao']}
        )
        tipos_fin.append(tipo)

    print("Tipos de financiamento criados/verificados")

    # Criar financiamentos
    financiamentos_data = [
        {
            'tipo': tipos_fin[0],  # Pronaf Custeio
            'nome': 'Financiamento Pronaf Custeio 2023',
            'valor': Decimal('150000.00'),
            'taxa': Decimal('4.5'),
            'parcelas': 60,
            'data_inicio': date(2023, 3, 1),
            'status': 'ATIVO'
        },
        {
            'tipo': tipos_fin[1],  # Pronaf Investimento
            'nome': 'Financiamento Pronaf Investimento 2024',
            'valor': Decimal('400000.00'),
            'taxa': Decimal('5.0'),
            'parcelas': 84,
            'data_inicio': date(2024, 6, 1),
            'status': 'ATIVO'
        },
        {
            'tipo': tipos_fin[2],  # FCO Custeio
            'nome': 'Financiamento FCO Safra 2024',
            'valor': Decimal('250000.00'),
            'taxa': Decimal('6.0'),
            'parcelas': 36,
            'data_inicio': date(2024, 9, 1),
            'status': 'ATIVO'
        },
    ]

    financiamentos_criados = 0
    for fin_data in financiamentos_data:
        try:
            financiamento, created = Financiamento.objects.get_or_create(
                propriedade=propriedade,
                nome=fin_data['nome'],
                defaults={
                    'tipo': fin_data['tipo'],
                    'valor_principal': fin_data['valor'],
                    'taxa_juros_anual': fin_data['taxa'],
                    'tipo_taxa': 'FIXA',
                    'data_contratacao': fin_data['data_inicio'],
                    'data_primeiro_vencimento': fin_data['data_inicio'].replace(day=15),
                    'data_ultimo_vencimento': fin_data['data_inicio'].replace(day=15, year=fin_data['data_inicio'].year + (fin_data['parcelas'] // 12)),
                    'numero_parcelas': fin_data['parcelas'],
                    'valor_parcela': (fin_data['valor'] * (1 + fin_data['taxa']/100)) / fin_data['parcelas'],
                    'ativo': fin_data['status'] == 'ATIVO',
                    'descricao': f'Financiamento {fin_data["tipo"].nome} para {propriedade.nome_propriedade}'
                }
            )
            if created:
                financiamentos_criados += 1
                print(f"  - {financiamento.nome} (R$ {financiamento.valor_principal:.2f})")
        except Exception as e:
            print(f"Erro ao criar financiamento {fin_data['nome']}: {e}")

    print(f"\nFinanciamentos criados: {financiamentos_criados}")

    # Criar projetos bancários
    projetos_data = [
        {
            'nome': 'Projeto Expansao Rebanho 2024',
            'tipo': 'INVESTIMENTO',
            'banco': 'Banco do Brasil',
            'valor': Decimal('600000.00'),
            'prazo': 96,
            'taxa': Decimal('7.5'),
            'status': 'APROVADO',
            'data_aprovacao': date(2024, 2, 15),
            'valor_aprovado': Decimal('600000.00'),
            'tipo_fin': tipos_fin[1]  # Pronaf Investimento
        },
        {
            'nome': 'Projeto Modernizacao Pastagens 2023',
            'tipo': 'INVESTIMENTO',
            'banco': 'Caixa Economica Federal',
            'valor': Decimal('350000.00'),
            'prazo': 72,
            'taxa': Decimal('6.5'),
            'status': 'CONTRATADO',
            'data_aprovacao': date(2023, 8, 10),
            'valor_aprovado': Decimal('350000.00'),
            'tipo_fin': tipos_fin[3]  # FCO Investimento
        },
        {
            'nome': 'Projeto Custeio Safra 2024/2025',
            'tipo': 'CUSTEIO',
            'banco': 'Banco do Brasil',
            'valor': Decimal('200000.00'),
            'prazo': 12,
            'taxa': Decimal('5.5'),
            'status': 'EM_ANALISE',
            'data_aprovacao': None,
            'valor_aprovado': None,
            'tipo_fin': tipos_fin[0]  # Pronaf Custeio
        },
    ]

    projetos_criados = 0
    for proj_data in projetos_data:
        data_solicitacao = proj_data['data_aprovacao'] - timedelta(days=60) if proj_data['data_aprovacao'] else date.today() - timedelta(days=30)

        try:
            projeto, created = ProjetoBancario.objects.get_or_create(
                propriedade=propriedade,
                nome_projeto=proj_data['nome'],
                defaults={
                    'tipo_projeto': proj_data['tipo'],
                    'banco_solicitado': proj_data['banco'],
                    'valor_solicitado': proj_data['valor'],
                    'prazo_pagamento': proj_data['prazo'],
                    'taxa_juros': proj_data['taxa'],
                    'data_solicitacao': data_solicitacao,
                    'data_aprovacao': proj_data['data_aprovacao'],
                    'valor_aprovado': proj_data['valor_aprovado'],
                    'status': proj_data['status'],
                    'observacoes': f'Projeto de {proj_data["tipo"].lower()} - {proj_data["nome"]}'
                }
            )
            if created:
                projetos_criados += 1
                status_desc = f" ({proj_data['status']})" if proj_data['status'] != 'EM_ANALISE' else " (Em analise)"
                print(f"  - {projeto.nome_projeto}{status_desc}")
        except Exception as e:
            print(f"Erro ao criar projeto {proj_data['nome']}: {e}")

    print(f"\nProjetos bancarios criados: {projetos_criados}")
    print("="*60)
    print("PROJETOS BANCARIOS POPULADOS COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
