#!/usr/bin/env python
"""
Script para popular dados dos módulos de Nutrição e Projetos Bancários
- Nutrição: TipoDistribuicao, DistribuicaoPasto, ControleCocho
- Projetos Bancários: TipoFinanciamento, Financiamento, ProjetoBancario
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestao_rural.models import Propriedade, PlanejamentoAnual, ProjetoBancario, TipoFinanciamento, Financiamento
from gestao_rural.models_controles_operacionais import TipoDistribuicao, DistribuicaoPasto, Pastagem, Cocho, ControleCocho

User = get_user_model()

def main():
    print("="*70)
    print("POPULANDO MODULOS NUTRICAO E PROJETOS BANCARIOS")
    print("="*70)
    
    # Buscar propriedade
    from gestao_rural.models import ProdutorRural
    produtor = ProdutorRural.objects.filter(cpf_cnpj='12.345.678/0001-90').first()
    if not produtor:
        print("ERRO: Produtor Monpec Agropecuaria Ltda nao encontrado!")
        return
    
    propriedade = Propriedade.objects.filter(nome_propriedade='Monpec', produtor=produtor).first()
    if not propriedade:
        print("ERRO: Propriedade Monpec nao encontrada!")
        return
    
    usuario = produtor.usuario_responsavel
    
    print(f"\nPropriedade: {propriedade.nome_propriedade}")
    print(f"Usuario: {usuario.username}\n")
    
    # 1. Criar tipos de distribuição
    print("[1/6] Criando tipos de distribuicao...")
    tipos_dist = criar_tipos_distribuicao()
    print(f"OK: {len(tipos_dist)} tipos criados\n")
    
    # 2. Criar distribuições no pasto
    print("[2/6] Criando distribuicoes no pasto...")
    distribuicoes = criar_distribuicoes_pasto(propriedade, tipos_dist, usuario)
    print(f"OK: {distribuicoes} distribuicoes criadas\n")
    
    # 3. Criar controles de cochos
    print("[3/6] Criando controles de cochos...")
    controles = criar_controles_cochos(propriedade, usuario)
    print(f"OK: {controles} controles criados\n")
    
    # 4. Criar tipos de financiamento
    print("[4/6] Criando tipos de financiamento...")
    tipos_fin = criar_tipos_financiamento()
    print(f"OK: {len(tipos_fin)} tipos criados\n")
    
    # 5. Criar financiamentos
    print("[5/6] Criando financiamentos...")
    financiamentos = criar_financiamentos(propriedade, tipos_fin)
    print(f"OK: {financiamentos} financiamentos criados\n")
    
    # 6. Criar projetos bancários
    print("[6/6] Criando projetos bancarios...")
    projetos = criar_projetos_bancarios(propriedade)
    print(f"OK: {projetos} projetos criados\n")
    
    # Resumo final
    print("="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Tipos Distribuicao: {TipoDistribuicao.objects.count()}")
    print(f"Distribuicoes Pasto: {DistribuicaoPasto.objects.filter(propriedade=propriedade).count()}")
    print(f"Controles Cochos: {ControleCocho.objects.filter(cocho__propriedade=propriedade).count()}")
    print(f"Tipos Financiamento: {TipoFinanciamento.objects.count()}")
    print(f"Financiamentos: {Financiamento.objects.filter(propriedade=propriedade).count()}")
    print(f"Projetos Bancarios: {ProjetoBancario.objects.filter(propriedade=propriedade).count()}")
    print("="*70)
    print("\nOK: DADOS POPULADOS COM SUCESSO!")

def criar_tipos_distribuicao():
    """Cria tipos de distribuição"""
    tipos_data = [
        {'nome': 'Sal Mineralizado', 'unidade': 'SC', 'descricao': 'Sal mineral para suplementação'},
        {'nome': 'Sal Comum', 'unidade': 'SC', 'descricao': 'Sal comum para consumo'},
        {'nome': 'Ração Concentrada', 'unidade': 'KG', 'descricao': 'Ração concentrada para engorda'},
        {'nome': 'Suplemento Proteinado', 'unidade': 'SC', 'descricao': 'Suplemento proteico'},
        {'nome': 'Ureia', 'unidade': 'KG', 'descricao': 'Ureia para suplementação'},
    ]
    
    tipos = []
    for tipo_data in tipos_data:
        tipo, created = TipoDistribuicao.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={
                'unidade_medida': tipo_data['unidade'],
                'descricao': tipo_data['descricao'],
                'ativo': True
            }
        )
        tipos.append(tipo)
    
    return tipos

def criar_distribuicoes_pasto(propriedade, tipos_dist, usuario):
    """Cria distribuições no pasto"""
    pastagens = Pastagem.objects.filter(propriedade=propriedade)
    if not pastagens.exists():
        print("AVISO: Nenhuma pastagem encontrada. Pulando distribuicoes.")
        return 0
    
    distribuicoes_criadas = 0
    
    # Criar distribuições dos últimos 6 meses
    for mes in range(6, 0, -1):
        num_dist = random.randint(3, 8)  # 3-8 distribuições por mês
        for _ in range(num_dist):
            data_dist = date.today() - timedelta(days=30 * mes + random.randint(0, 29))
            pastagem = random.choice(list(pastagens))
            tipo_dist = random.choice(tipos_dist)
            
            # Quantidade baseada no tipo
            if tipo_dist.unidade_medida == 'SC':
                quantidade = Decimal(str(random.randint(5, 30)))  # Sacas
            else:
                quantidade = Decimal(str(random.randint(100, 1000)))  # KG
            
            numero_animais = random.randint(50, 300)
            valor_unitario = Decimal(str(random.randint(30, 100)))
            
            distribuicao, created = DistribuicaoPasto.objects.get_or_create(
                propriedade=propriedade,
                pastagem=pastagem,
                tipo_distribuicao=tipo_dist,
                data_distribuicao=data_dist,
                defaults={
                    'quantidade': quantidade,
                    'numero_animais': numero_animais,
                    'valor_unitario': valor_unitario,
                    'valor_total': quantidade * valor_unitario,
                    'responsavel': usuario,
                    'observacoes': f'Distribuicao em {pastagem.nome}'
                }
            )
            if created:
                distribuicoes_criadas += 1
    
    return distribuicoes_criadas

def criar_controles_cochos(propriedade, usuario):
    """Cria controles de cochos"""
    cochos = Cocho.objects.filter(propriedade=propriedade, status='ATIVO')
    if not cochos.exists():
        print("AVISO: Nenhum cocho ativo encontrado. Pulando controles.")
        return 0
    
    controles_criados = 0
    
    # Criar controles dos últimos 3 meses
    for mes in range(3, 0, -1):
        num_controles = random.randint(10, 20)  # 10-20 controles por mês
        for _ in range(num_controles):
            data_controle = date.today() - timedelta(days=30 * mes + random.randint(0, 29))
            cocho = random.choice(list(cochos))
            
            quantidade_abastecida = Decimal(str(random.randint(50, 500)))
            quantidade_restante = Decimal(str(random.randint(0, int(quantidade_abastecida * Decimal('0.5')))))
            quantidade_consumida = quantidade_abastecida - quantidade_restante
            numero_animais = random.randint(20, 150)
            
            valor_unitario = Decimal(str(random.randint(2, 10)))  # Preço por kg/litro
            
            controle, created = ControleCocho.objects.get_or_create(
                cocho=cocho,
                data=data_controle,
                defaults={
                    'quantidade_abastecida': quantidade_abastecida,
                    'quantidade_restante': quantidade_restante,
                    'quantidade_consumida': quantidade_consumida,
                    'numero_animais': numero_animais,
                    'consumo_por_animal': quantidade_consumida / Decimal(str(numero_animais)) if numero_animais > 0 else Decimal('0'),
                    'valor_unitario': valor_unitario,
                    'valor_total_consumido': quantidade_consumida * valor_unitario,
                    'observacoes': f'Controle diario do cocho {cocho.nome}',
                    'responsavel': usuario
                }
            )
            if created:
                controles_criados += 1
    
    return controles_criados

def criar_tipos_financiamento():
    """Cria tipos de financiamento"""
    tipos_data = [
        {'nome': 'Pronaf - Custeio', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Custeio'},
        {'nome': 'Pronaf - Investimento', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Investimento'},
        {'nome': 'Pronamp - Custeio', 'descricao': 'Programa Nacional de Apoio ao Médio Produtor Rural - Custeio'},
        {'nome': 'Pronamp - Investimento', 'descricao': 'Programa Nacional de Apoio ao Médio Produtor Rural - Investimento'},
        {'nome': 'FCO - Custeio', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Custeio'},
        {'nome': 'FCO - Investimento', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Investimento'},
        {'nome': 'Crédito Rural Privado', 'descricao': 'Crédito rural oferecido por bancos privados'},
    ]
    
    tipos = []
    for tipo_data in tipos_data:
        tipo, created = TipoFinanciamento.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={'descricao': tipo_data['descricao']}
        )
        tipos.append(tipo)
    
    return tipos

def criar_financiamentos(propriedade, tipos_fin):
    """Cria financiamentos"""
    financiamentos_criados = 0
    
    # Criar 2-3 financiamentos ativos
    for i in range(random.randint(2, 3)):
        tipo_fin = random.choice(tipos_fin)
        data_contratacao = date.today() - timedelta(days=random.randint(180, 1095))  # 6 meses a 3 anos atrás
        
        valor_principal = Decimal(str(random.randint(50000, 500000)))
        taxa_juros = Decimal(str(random.uniform(4.5, 8.5))).quantize(Decimal('0.01'))
        numero_parcelas = random.choice([12, 24, 36, 48, 60])
        
        # Calcular valor da parcela (simplificado)
        taxa_mensal = taxa_juros / Decimal('12') / Decimal('100')
        valor_parcela = valor_principal * (taxa_mensal * (1 + taxa_mensal) ** numero_parcelas) / ((1 + taxa_mensal) ** numero_parcelas - 1)
        
        data_primeiro_venc = data_contratacao + timedelta(days=30)
        data_ultimo_venc = data_primeiro_venc + timedelta(days=30 * numero_parcelas)
        
        nome_fin = f"{tipo_fin.nome} - {data_contratacao.year}"
        
        financiamento, created = Financiamento.objects.get_or_create(
            propriedade=propriedade,
            tipo=tipo_fin,
            nome=nome_fin,
            defaults={
                'valor_principal': valor_principal,
                'taxa_juros_anual': taxa_juros,
                'tipo_taxa': random.choice(['FIXA', 'VARIAVEL']),
                'data_contratacao': data_contratacao,
                'data_primeiro_vencimento': data_primeiro_venc,
                'data_ultimo_vencimento': data_ultimo_venc,
                'numero_parcelas': numero_parcelas,
                'valor_parcela': valor_parcela.quantize(Decimal('0.01')),
                'ativo': True,
                'descricao': f'Financiamento {tipo_fin.nome} para {propriedade.nome_propriedade}'
            }
        )
        if created:
            financiamentos_criados += 1
    
    return financiamentos_criados

def criar_projetos_bancarios(propriedade):
    """Cria projetos bancários"""
    projetos_criados = 0
    
    # Buscar planejamento anual se existir
    planejamento = PlanejamentoAnual.objects.filter(propriedade=propriedade).first()
    
    projetos_data = [
        {
            'nome': 'Projeto de Custeio - Safra 2024/2025',
            'tipo': 'CUSTEIO',
            'banco': 'Banco do Brasil',
            'valor': Decimal('150000.00'),
            'prazo': 12,
            'taxa': Decimal('6.5'),
            'status': 'APROVADO',
            'data_aprovacao': date.today() - timedelta(days=60),
            'valor_aprovado': Decimal('150000.00')
        },
        {
            'nome': 'Projeto de Investimento - Expansão de Rebanho',
            'tipo': 'INVESTIMENTO',
            'banco': 'Banco do Brasil',
            'valor': Decimal('500000.00'),
            'prazo': 60,
            'taxa': Decimal('7.0'),
            'status': 'EM_ANALISE',
            'data_aprovacao': None,
            'valor_aprovado': None
        },
        {
            'nome': 'Projeto de Comercialização - Venda de Gado',
            'tipo': 'COMERCIALIZACAO',
            'banco': 'Caixa Econômica Federal',
            'valor': Decimal('300000.00'),
            'prazo': 8,
            'taxa': Decimal('5.5'),
            'status': 'CONTRATADO',
            'data_aprovacao': date.today() - timedelta(days=30),
            'valor_aprovado': Decimal('300000.00')
        },
    ]
    
    for proj_data in projetos_data:
        data_solicitacao = date.today() - timedelta(days=random.randint(90, 180))
        
        projeto, created = ProjetoBancario.objects.get_or_create(
            propriedade=propriedade,
            nome_projeto=proj_data['nome'],
            defaults={
                'planejamento': planejamento,
                'tipo_projeto': proj_data['tipo'],
                'banco_solicitado': proj_data['banco'],
                'valor_solicitado': proj_data['valor'],
                'prazo_pagamento': proj_data['prazo'],
                'taxa_juros': proj_data['taxa'],
                'data_solicitacao': data_solicitacao,
                'data_aprovacao': proj_data['data_aprovacao'],
                'valor_aprovado': proj_data['valor_aprovado'],
                'status': proj_data['status'],
                'observacoes': f'Projeto {proj_data["tipo"]} para {propriedade.nome_propriedade}'
            }
        )
        if created:
            projetos_criados += 1
    
    return projetos_criados

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

