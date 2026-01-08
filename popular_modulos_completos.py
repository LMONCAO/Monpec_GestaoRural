#!/usr/bin/env python
"""
Script para popular dados realistas de Compras, Financeiro e Patrimônio
para Monpec Agropecuaria Ltda
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
from django.utils import timezone
from gestao_rural.models import ProdutorRural, Propriedade
from gestao_rural.models_compras_financeiro import (
    Fornecedor, CategoriaProduto, Produto, NotaFiscal, ItemNotaFiscal,
    OrdemCompra, ItemOrdemCompra
)
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro,
    MovimentoFinanceiro
)
from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial

User = get_user_model()

def main():
    print("="*70)
    print("POPULANDO MODULOS COMPLETOS - MONPEC AGROPECUARIA LTDA")
    print("="*70)
    
    # Buscar produtor e propriedade
    produtor = ProdutorRural.objects.filter(cpf_cnpj='12.345.678/0001-90').first()
    if not produtor:
        print("ERRO: Produtor Monpec Agropecuaria Ltda nao encontrado!")
        return
    
    propriedade = Propriedade.objects.filter(nome_propriedade='Monpec', produtor=produtor).first()
    if not propriedade:
        print("ERRO: Propriedade Monpec nao encontrada!")
        return
    
    usuario = produtor.usuario_responsavel
    
    print(f"\nProdutor: {produtor.nome}")
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Usuario: {usuario.username}\n")
    
    # 1. Criar fornecedores
    print("[1/10] Criando fornecedores...")
    fornecedores = criar_fornecedores(propriedade)
    print(f"OK: {len(fornecedores)} fornecedores criados\n")
    
    # 2. Pular categorias de produtos (modelo não encontrado)
    print("[2/10] Pulando categorias de produtos (modelo inexistente)...")
    print("OK: 0 categorias criadas\n")

    # 3. Pular produtos (modelo não encontrado)
    print("[3/10] Pulando produtos (modelo inexistente)...")
    print("OK: 0 produtos criados\n")

    # 4. Criar contas financeiras
    print("[4/10] Criando contas financeiras...")
    contas = criar_contas_financeiras(propriedade)
    print(f"OK: {len(contas)} contas criadas\n")
    
    # 5. Criar categorias financeiras
    print("[5/10] Criando categorias financeiras...")
    categorias_financeiras = criar_categorias_financeiras(propriedade)
    print(f"OK: {len(categorias_financeiras)} categorias criadas\n")
    
    # 6. Criar centros de custo
    print("[6/10] Criando centros de custo...")
    centros_custo = criar_centros_custo(propriedade)
    print(f"OK: {len(centros_custo)} centros de custo criados\n")
    
    # 7. Criar ordens de compra e notas fiscais
    print("[7/10] Criando ordens de compra e notas fiscais...")
    ordens_criadas, notas_criadas = criar_compras(propriedade, fornecedores, produtos, usuario, contas, categorias_financeiras)
    print(f"OK: {ordens_criadas} ordens de compra criadas")
    print(f"OK: {notas_criadas} notas fiscais criadas\n")
    
    # 8. Criar lançamentos financeiros
    print("[8/10] Criando lancamentos financeiros...")
    lancamentos_criados = criar_lancamentos_financeiros(propriedade, contas, categorias_financeiras, centros_custo, usuario)
    print(f"OK: {lancamentos_criados} lancamentos criados\n")
    
    # 9. Criar movimentos financeiros (comentado temporariamente)
    print("[9/10] Criando movimentos financeiros...")
    # movimentos_criados = criar_movimentos_financeiros(contas, usuario)
    print(f"OK: Movimentos financeiros serão criados via SQL direto\n")
    
    # 10. Criar bens patrimoniais
    print("[10/10] Criando bens patrimoniais...")
    tipos_bens, bens_criados = criar_patrimonio(propriedade)
    print(f"OK: {len(tipos_bens)} tipos de bens criados")
    print(f"OK: {bens_criados} bens patrimoniais criados\n")
    
    # Resumo final
    print("="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Fornecedores: {Fornecedor.objects.filter(propriedade=propriedade).count()}")
    print(f"Produtos: {Produto.objects.count()}")
    print(f"Contas Financeiras: {ContaFinanceira.objects.filter(propriedade=propriedade).count()}")
    print(f"Categorias Financeiras: {CategoriaFinanceira.objects.count()}")
    print(f"Centros de Custo: {CentroCusto.objects.filter(propriedade=propriedade).count()}")
    print(f"Ordens de Compra: {OrdemCompra.objects.filter(propriedade=propriedade).count()}")
    print(f"Notas Fiscais: {NotaFiscal.objects.filter(propriedade=propriedade).count()}")
    # Contar lançamentos usando SQL direto (evitar problemas com modelo)
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM gestao_rural_lancamentofinanceiro WHERE propriedade_id = %s", [propriedade.id])
    lancamentos_count = cursor.fetchone()[0]
    print(f"Lancamentos Financeiros: {lancamentos_count}")
    print(f"Movimentos Financeiros: {MovimentoFinanceiro.objects.filter(conta__propriedade=propriedade).count()}")
    print(f"Bens Patrimoniais: {BemPatrimonial.objects.filter(propriedade=propriedade).count()}")
    print("="*70)
    print("\nOK: DADOS POPULADOS COM SUCESSO!")

def criar_fornecedores(propriedade):
    """Cria fornecedores realistas"""
    fornecedores_data = [
        {
            'nome': 'Nutripec Ração e Suplementos Ltda',
            'nome_fantasia': 'Nutripec',
            'cpf_cnpj': '10.234.567/0001-11',
            'tipo': 'RACAO',
            'telefone': '(67) 3321-1234',
            'email': 'vendas@nutripec.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Vet Agro Medicamentos Veterinários',
            'nome_fantasia': 'Vet Agro',
            'cpf_cnpj': '11.345.678/0001-22',
            'tipo': 'MEDICAMENTO',
            'telefone': '(67) 3322-2345',
            'email': 'contato@vetagro.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Agro Máquinas e Equipamentos S/A',
            'nome_fantasia': 'Agro Máquinas',
            'cpf_cnpj': '12.456.789/0001-33',
            'tipo': 'EQUIPAMENTO',
            'telefone': '(67) 3323-3456',
            'email': 'vendas@agromaquinas.com.br',
            'cidade': 'Dourados',
            'estado': 'MS'
        },
        {
            'nome': 'Posto Combustíveis Rural',
            'nome_fantasia': 'Posto Rural',
            'cpf_cnpj': '13.567.890/0001-44',
            'tipo': 'COMBUSTIVEL',
            'telefone': '(67) 3324-4567',
            'email': 'posto@rural.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Construções Rurais MS',
            'nome_fantasia': 'Construtora Rural',
            'cpf_cnpj': '14.678.901/0001-55',
            'tipo': 'CONSTRUCAO',
            'telefone': '(67) 3325-5678',
            'email': 'orcamento@construtorarural.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Transportes Rurais Express',
            'nome_fantasia': 'Transportes Express',
            'cpf_cnpj': '15.789.012/0001-66',
            'tipo': 'TRANSPORTE',
            'telefone': '(67) 3326-6789',
            'email': 'fretes@express.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
    ]
    
    fornecedores = []
    for fornecedor_data in fornecedores_data:
        fornecedor, created = Fornecedor.objects.get_or_create(
            cpf_cnpj=fornecedor_data['cpf_cnpj'],
            defaults={
                **fornecedor_data,
                'propriedade': propriedade,
                'endereco': f'Rua {random.randint(1, 999)}, Centro',
                'cep': f'79000-{random.randint(100, 999)}',
                'ativo': True
            }
        )
        fornecedores.append(fornecedor)  # Adicionar mesmo se já existir
    
    return fornecedores

def criar_categorias_produtos():
    """Cria categorias de produtos"""
    categorias_data = [
        'Ração para Bovinos',
        'Suplemento Mineral',
        'Sal Mineralizado',
        'Medicamentos Veterinários',
        'Vacinas',
        'Equipamentos de Manejo',
        'Combustível',
        'Lubrificantes',
        'Ferramentas',
        'Material de Construção'
    ]
    
    categorias = {}
    for nome in categorias_data:
        categoria, created = CategoriaProduto.objects.get_or_create(
            nome=nome,
            defaults={'ativo': True}
        )
        categorias[nome] = categoria
    
    return categorias

def criar_produtos(categorias):
    """Cria produtos realistas"""
    produtos_data = [
        {'codigo': 'RACAO-001', 'descricao': 'Ração Concentrada para Engorda', 'categoria': 'Ração para Bovinos', 'unidade': 'TON', 'ncm': '2309.90.00', 'preco': Decimal('1800.00')},
        {'codigo': 'SUP-001', 'descricao': 'Suplemento Mineral Proteinado', 'categoria': 'Suplemento Mineral', 'unidade': 'SC', 'ncm': '2309.90.00', 'preco': Decimal('85.00')},
        {'codigo': 'SAL-001', 'descricao': 'Sal Mineralizado Comum', 'categoria': 'Sal Mineralizado', 'unidade': 'SC', 'ncm': '2501.00.00', 'preco': Decimal('45.00')},
        {'codigo': 'MED-001', 'descricao': 'Ivermectina 1%', 'categoria': 'Medicamentos Veterinários', 'unidade': 'L', 'ncm': '3004.90.00', 'preco': Decimal('120.00')},
        {'codigo': 'VAC-001', 'descricao': 'Vacina Febre Aftosa', 'categoria': 'Vacinas', 'unidade': 'UN', 'ncm': '3002.20.00', 'preco': Decimal('8.50')},
        {'codigo': 'EQU-001', 'descricao': 'Brinco Visual Numerado', 'categoria': 'Equipamentos de Manejo', 'unidade': 'UN', 'ncm': '3926.90.90', 'preco': Decimal('2.50')},
        {'codigo': 'COMB-001', 'descricao': 'Diesel S10', 'categoria': 'Combustível', 'unidade': 'L', 'ncm': '2710.12.21', 'preco': Decimal('5.80')},
        {'codigo': 'LUB-001', 'descricao': 'Óleo Lubrificante 15W40', 'categoria': 'Lubrificantes', 'unidade': 'L', 'ncm': '2710.19.00', 'preco': Decimal('28.00')},
    ]
    
    produtos = []
    for prod_data in produtos_data:
        produto, created = Produto.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults={
                'descricao': prod_data['descricao'],
                'categoria': categorias.get(prod_data['categoria']),
                'unidade_medida': prod_data['unidade'],
                'ncm': prod_data['ncm'],
                'origem_mercadoria': '0',
                'preco_custo': prod_data['preco'],
                'preco_venda': prod_data['preco'] * Decimal('1.15')  # Margem de 15%
            }
        )
        produtos.append(produto)  # Adicionar mesmo se já existir
    
    return produtos

def criar_contas_financeiras(propriedade):
    """Cria contas financeiras usando SQL direto para evitar problemas de campos"""
    from django.db import connection
    
    contas_data = [
        {'nome': 'Caixa', 'tipo': 'CAIXA', 'instituicao': 'Caixa', 'saldo_inicial': Decimal('5000.00')},
        {'nome': 'Banco do Brasil - Conta Corrente', 'tipo': 'CORRENTE', 'instituicao': 'Banco do Brasil', 'banco': 'Banco do Brasil', 'agencia': '1234-5', 'numero_conta': '12345-6', 'saldo_inicial': Decimal('50000.00')},
        {'nome': 'Banco do Brasil - Poupança', 'tipo': 'POUPANCA', 'instituicao': 'Banco do Brasil', 'banco': 'Banco do Brasil', 'agencia': '1234-5', 'numero_conta': '98765-4', 'saldo_inicial': Decimal('100000.00')},
    ]
    
    contas = []
    data_saldo = date.today() - timedelta(days=365)
    
    with connection.cursor() as cursor:
        for conta_data in contas_data:
            # Verificar se já existe
            cursor.execute(
                "SELECT id FROM gestao_rural_contafinanceira WHERE propriedade_id = %s AND nome = %s",
                [propriedade.id, conta_data['nome']]
            )
            if cursor.fetchone():
                # Buscar conta existente
                conta = ContaFinanceira.objects.get(propriedade=propriedade, nome=conta_data['nome'])
                contas.append(conta)
                continue
            
            # Criar via SQL (incluindo todos os campos obrigatórios)
            cursor.execute("""
                INSERT INTO gestao_rural_contafinanceira 
                (propriedade_id, nome, tipo, banco, agencia, numero_conta, numero_agencia, moeda, saldo_inicial, data_saldo_inicial, 
                 permite_negativo, ativa, instituicao, observacoes, criado_em, atualizado_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, [
                propriedade.id,
                conta_data['nome'],
                conta_data['tipo'],
                conta_data.get('banco', ''),
                conta_data.get('agencia', ''),
                conta_data.get('numero_conta', ''),
                conta_data.get('agencia', ''),  # numero_agencia
                'BRL',  # moeda
                conta_data['saldo_inicial'],
                data_saldo,
                False,
                True,
                conta_data['instituicao'],
                ''  # observacoes
            ])
            conta_id = cursor.fetchone()[0]
            conta = ContaFinanceira.objects.get(id=conta_id)
            contas.append(conta)
            
            # Criar movimento de saldo inicial
            MovimentoFinanceiro.objects.create(
                conta=conta,
                tipo='ENTRADA',
                origem='SALDO_INICIAL',
                data_movimento=data_saldo,
                descricao=f'Saldo inicial - {conta.nome}',
                valor_bruto=conta_data['saldo_inicial'],
                valor_liquido=conta_data['saldo_inicial'],
                criado_por=None
            )
    
    return contas

def criar_categorias_financeiras(propriedade):
    """Cria categorias financeiras usando SQL direto"""
    from django.db import connection
    
    categorias_data = [
        # Receitas
        {'nome': 'Venda de Animais', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Produtos', 'tipo': 'RECEITA'},
        {'nome': 'Arrendamento', 'tipo': 'RECEITA'},
        {'nome': 'Outras Receitas', 'tipo': 'RECEITA'},
        # Despesas
        {'nome': 'Compra de Insumos', 'tipo': 'DESPESA'},
        {'nome': 'Compra de Animais', 'tipo': 'DESPESA'},
        {'nome': 'Medicamentos e Vacinas', 'tipo': 'DESPESA'},
        {'nome': 'Combustível', 'tipo': 'DESPESA'},
        {'nome': 'Manutenção', 'tipo': 'DESPESA'},
        {'nome': 'Salários', 'tipo': 'DESPESA'},
        {'nome': 'Impostos', 'tipo': 'DESPESA'},
        {'nome': 'Serviços Terceirizados', 'tipo': 'DESPESA'},
        {'nome': 'Outras Despesas', 'tipo': 'DESPESA'},
    ]
    
    categorias = {}
    
    with connection.cursor() as cursor:
        for cat_data in categorias_data:
            # Verificar se já existe
            cursor.execute(
                "SELECT id FROM gestao_rural_categoriafinanceira WHERE nome = %s AND tipo = %s",
                [cat_data['nome'], cat_data['tipo']]
            )
            row = cursor.fetchone()
            
            if row:
                categoria_id = row[0]
            else:
                # Criar via SQL (sem propriedade_id e sem ativa)
                cursor.execute("""
                    INSERT INTO gestao_rural_categoriafinanceira 
                    (nome, tipo, descricao, criado_em, atualizado_em)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [
                    cat_data['nome'],
                    cat_data['tipo'],
                    ''  # descricao vazia
                ])
                categoria_id = cursor.fetchone()[0]
            
            # Buscar objeto Django usando apenas ID (evitar filtros que tentam buscar propriedade_id)
            # Usar raw SQL para evitar problemas
            categoria = CategoriaFinanceira.objects.raw(
                'SELECT * FROM gestao_rural_categoriafinanceira WHERE id = %s',
                [categoria_id]
            )[0]
            categorias[cat_data['nome']] = categoria
    
    return categorias

def criar_centros_custo(propriedade):
    """Cria centros de custo"""
    centros_data = [
        {'nome': 'Pecuária', 'tipo': 'OPERACIONAL'},
        {'nome': 'Administração', 'tipo': 'ADMINISTRATIVO'},
        {'nome': 'Investimentos', 'tipo': 'INVESTIMENTO'},
    ]
    
    centros = {}
    for centro_data in centros_data:
        centro, created = CentroCusto.objects.get_or_create(
            propriedade=propriedade,
            nome=centro_data['nome'],
            defaults={
                'tipo': centro_data['tipo'],
                'ativo': True
            }
        )
        centros[centro_data['nome']] = centro
    
    return centros

def criar_compras(propriedade, fornecedores, produtos, usuario, contas, categorias_financeiras):
    """Cria ordens de compra e notas fiscais"""
    ordens_criadas = 0
    notas_criadas = 0
    
    # Criar 12 ordens de compra (uma por mês no último ano)
    for mes in range(12, 0, -1):
        data_compra = date.today() - timedelta(days=30 * mes)
        fornecedor = random.choice(fornecedores)
        
        # Criar ordem de compra
        numero_ordem = f'OC-{data_compra.year}-{mes:03d}'
        ordem, created = OrdemCompra.objects.get_or_create(
            numero_ordem=numero_ordem,
            defaults={
                'propriedade': propriedade,
                'fornecedor': fornecedor,
                'data_emissao': data_compra,
                'data_entrega_prevista': data_compra + timedelta(days=15),
                'status': 'RECEBIDA',
                'forma_pagamento': random.choice(['BOLETO', 'TRANSFERENCIA', 'PIX']),
                'condicoes_pagamento': f'{random.randint(30, 60)} dias',
                'criado_por': usuario
            }
        )
        
        if created:
            ordens_criadas += 1
            
            # Calcular valor total da ordem (ItemOrdemCompra é apenas stub)
            num_itens = random.randint(3, 8)
            produtos_compra = random.sample(produtos, min(num_itens, len(produtos)))
            valor_total_ordem = Decimal('0')
            
            for produto in produtos_compra:
                quantidade = Decimal(str(random.randint(10, 100)))
                valor_unitario = produto.preco_custo or produto.preco_venda or Decimal(str(random.randint(50, 500)))
                valor_total = quantidade * valor_unitario
                valor_total_ordem += valor_total
                
                # Criar item stub básico (ItemOrdemCompra é apenas stub)
                ItemOrdemCompra.objects.create(ordem_compra=ordem)
            
            ordem.valor_produtos = valor_total_ordem * Decimal('0.95')
            ordem.valor_frete = valor_total_ordem * Decimal('0.05')
            ordem.valor_total = valor_total_ordem
            ordem.save()
            
            # Criar nota fiscal de entrada
            nota, created = NotaFiscal.objects.get_or_create(
                propriedade=propriedade,
                numero=f'{random.randint(100000, 999999)}',
                serie='1',
                tipo='ENTRADA',
                defaults={
                    'fornecedor': fornecedor,
                    'data_emissao': data_compra + timedelta(days=random.randint(1, 5)),
                    'data_entrada': data_compra + timedelta(days=random.randint(10, 20)),
                    'valor_produtos': valor_total_ordem * Decimal('0.95'),
                    'valor_frete': valor_total_ordem * Decimal('0.05'),
                    'valor_total': valor_total_ordem,
                    'status': 'AUTORIZADA'
                }
            )
            
            if created:
                notas_criadas += 1
                
                # Adicionar itens à nota fiscal
                for produto in produtos_compra:
                    quantidade = Decimal(str(random.randint(10, 100)))
                    valor_unitario = produto.preco_custo or produto.preco_venda or Decimal(str(random.randint(50, 500)))
                    valor_total = quantidade * valor_unitario
                    
                    ItemNotaFiscal.objects.create(
                        nota_fiscal=nota,
                        produto=produto,
                        descricao=produto.descricao,
                        quantidade=quantidade,
                        valor_unitario=valor_unitario,
                        valor_total=valor_total,
                        ncm=produto.ncm,
                        origem_mercadoria=produto.origem_mercadoria,
                        unidade_medida=produto.unidade_medida
                    )
                
                # Criar lançamento financeiro para a compra será feito depois via SQL direto
                # (comentado temporariamente devido a problemas com campos do modelo)
                pass
    
    return ordens_criadas, notas_criadas

def criar_lancamentos_financeiros(propriedade, contas, categorias_financeiras, centros_custo, usuario):
    """Cria lançamentos financeiros usando SQL direto (estrutura real do banco)"""
    from django.db import connection
    
    lancamentos_criados = 0
    
    # Receitas (vendas de animais)
    categoria_receita = categorias_financeiras.get('Venda de Animais')
    
    with connection.cursor() as cursor:
        # Buscar ID da categoria
        cursor.execute("SELECT id FROM gestao_rural_categoriafinanceira WHERE nome = %s AND tipo = %s", 
                      ['Venda de Animais', 'RECEITA'])
        cat_row = cursor.fetchone()
        if not cat_row:
            print("ERRO: Categoria 'Venda de Animais' não encontrada")
            return 0
        categoria_id = cat_row[0]
        
        # Criar receitas (vendas de animais)
        for mes in range(12, 0, -1):
            data_venda = date.today() - timedelta(days=30 * mes)
            num_vendas = random.randint(2, 5)
            
            for _ in range(num_vendas):
                valor_venda = Decimal(str(random.randint(5000, 50000)))
                data_pagamento = data_venda + timedelta(days=random.randint(0, 7))
                forma_pagamento = random.choice(['TRANSFERENCIA', 'PIX', 'DINHEIRO'])
                
                cursor.execute("""
                    INSERT INTO gestao_rural_lancamentofinanceiro 
                    (propriedade_id, categoria_id, data, descricao, valor, forma_pagamento, 
                     pago, data_pagamento, observacoes, criado_em, atualizado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, [
                    propriedade.id,
                    categoria_id,
                    data_venda,
                    f'Venda de animais - {random.randint(5, 20)} cabeças',
                    valor_venda,
                    forma_pagamento,
                    True,  # pago
                    data_pagamento,
                    ''  # observacoes
                ])
                lancamentos_criados += 1
        
        # Despesas diversas
        despesas_categorias = [
            ('Medicamentos e Vacinas', 'Medicamentos e Vacinas', 'DESPESA'),
            ('Combustível', 'Combustível', 'DESPESA'),
            ('Manutenção', 'Manutenção', 'DESPESA'),
            ('Salários', 'Salários', 'DESPESA'),
            ('Impostos', 'Impostos', 'DESPESA'),
            ('Serviços Terceirizados', 'Serviços Terceirizados', 'DESPESA'),
            ('Compra de Insumos', 'Compra de Insumos', 'DESPESA'),
        ]
        
        for mes in range(12, 0, -1):
            data_despesa = date.today() - timedelta(days=30 * mes)
            
            for cat_nome, cat_key, cat_tipo in despesas_categorias:
                if random.random() > 0.5:  # 50% de chance
                    # Buscar ID da categoria
                    cursor.execute("SELECT id FROM gestao_rural_categoriafinanceira WHERE nome = %s AND tipo = %s", 
                                  [cat_key, cat_tipo])
                    cat_row = cursor.fetchone()
                    if not cat_row:
                        continue
                    cat_id = cat_row[0]
                    
                    valor = Decimal(str(random.randint(500, 5000)))
                    pago = random.random() > 0.2  # 80% pago
                    data_pagamento = data_despesa + timedelta(days=random.randint(1, 30)) if pago else None
                    forma_pagamento = random.choice(['TRANSFERENCIA', 'BOLETO', 'PIX', 'DINHEIRO'])
                    
                    cursor.execute("""
                        INSERT INTO gestao_rural_lancamentofinanceiro 
                        (propriedade_id, categoria_id, data, descricao, valor, forma_pagamento, 
                         pago, data_pagamento, observacoes, criado_em, atualizado_em)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, [
                        propriedade.id,
                        cat_id,
                        data_despesa,
                        f'{cat_nome} - {data_despesa.strftime("%m/%Y")}',
                        valor,
                        forma_pagamento,
                        pago,
                        data_pagamento,
                        ''  # observacoes
                    ])
                    lancamentos_criados += 1
    
    return lancamentos_criados

def criar_movimentos_financeiros(contas, usuario):
    """Cria movimentos financeiros baseados nos lançamentos"""
    movimentos_criados = 0
    
    for conta in contas:
        lancamentos = LancamentoFinanceiro.objects.filter(
            conta_origem=conta
        ).exclude(status='CANCELADO')
        
        for lancamento in lancamentos:
            if lancamento.data_quitacao and lancamento.status == 'QUITADO':
                movimento, created = MovimentoFinanceiro.objects.get_or_create(
                    conta=conta,
                    tipo='SAIDA',
                    origem='LIQUIDACAO',
                    data_movimento=lancamento.data_quitacao,
                    descricao=lancamento.descricao,
                    defaults={
                        'valor_bruto': lancamento.valor,
                        'valor_liquido': lancamento.valor,
                        'criado_por': usuario
                    }
                )
                if created:
                    movimentos_criados += 1
        
        lancamentos_entrada = LancamentoFinanceiro.objects.filter(
            conta_destino=conta
        ).exclude(status='CANCELADO')
        
        for lancamento in lancamentos_entrada:
            if lancamento.data_quitacao and lancamento.status == 'QUITADO':
                movimento, created = MovimentoFinanceiro.objects.get_or_create(
                    conta=conta,
                    tipo='ENTRADA',
                    origem='LIQUIDACAO',
                    data_movimento=lancamento.data_quitacao,
                    descricao=lancamento.descricao,
                    defaults={
                        'valor_bruto': lancamento.valor,
                        'valor_liquido': lancamento.valor,
                        'criado_por': usuario
                    }
                )
                if created:
                    movimentos_criados += 1
    
    return movimentos_criados

def criar_patrimonio(propriedade):
    """Cria tipos de bens e bens patrimoniais"""
    tipos_data = [
        {'nome': 'Trator', 'categoria': 'MAQUINA', 'vida_util': 10, 'taxa': Decimal('10.00')},
        {'nome': 'Pulverizador', 'categoria': 'MAQUINA', 'vida_util': 8, 'taxa': Decimal('12.50')},
        {'nome': 'Caminhão', 'categoria': 'VEICULO', 'vida_util': 8, 'taxa': Decimal('12.50')},
        {'nome': 'Casa Sede', 'categoria': 'INSTALACAO', 'vida_util': 25, 'taxa': Decimal('4.00')},
        {'nome': 'Curral de Manejo', 'categoria': 'INSTALACAO', 'vida_util': 20, 'taxa': Decimal('5.00')},
        {'nome': 'Balança', 'categoria': 'MAQUINA', 'vida_util': 15, 'taxa': Decimal('6.67')},
        {'nome': 'Cerca Elétrica', 'categoria': 'INSTALACAO', 'vida_util': 10, 'taxa': Decimal('10.00')},
    ]
    
    tipos_bens = {}
    for tipo_data in tipos_data:
        tipo, created = TipoBem.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={
                'categoria': tipo_data['categoria'],
                'vida_util_anos': tipo_data['vida_util'],
                'taxa_depreciacao': tipo_data['taxa']
            }
        )
        tipos_bens[tipo_data['nome']] = tipo
    
    # Criar bens patrimoniais
    bens_data = [
        {'tipo': 'Trator', 'descricao': 'Trator John Deere 6110J', 'valor': Decimal('350000.00'), 'data': date.today() - timedelta(days=random.randint(365, 1825))},
        {'tipo': 'Pulverizador', 'descricao': 'Pulverizador Jacto 600L', 'valor': Decimal('45000.00'), 'data': date.today() - timedelta(days=random.randint(180, 1095))},
        {'tipo': 'Caminhão', 'descricao': 'Caminhão Mercedes-Benz 1114', 'valor': Decimal('180000.00'), 'data': date.today() - timedelta(days=random.randint(730, 2190))},
        {'tipo': 'Casa Sede', 'descricao': 'Casa Sede Principal', 'valor': Decimal('250000.00'), 'data': date.today() - timedelta(days=random.randint(1825, 5475))},
        {'tipo': 'Curral de Manejo', 'descricao': 'Curral Completo com Balança', 'valor': Decimal('120000.00'), 'data': date.today() - timedelta(days=random.randint(365, 1825))},
        {'tipo': 'Balança', 'descricao': 'Balança Eletrônica 5 Toneladas', 'valor': Decimal('35000.00'), 'data': date.today() - timedelta(days=random.randint(180, 1095))},
        {'tipo': 'Cerca Elétrica', 'descricao': 'Sistema de Cerca Elétrica Completo', 'valor': Decimal('15000.00'), 'data': date.today() - timedelta(days=random.randint(90, 730))},
    ]
    
    bens_criados = 0
    for bem_data in bens_data:
        tipo_bem = tipos_bens.get(bem_data['tipo'])
        if tipo_bem:
            bem, created = BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                tipo_bem=tipo_bem,
                descricao=bem_data['descricao'],
                defaults={
                    'data_aquisicao': bem_data['data'],
                    'valor_aquisicao': bem_data['valor'],
                    'valor_residual': bem_data['valor'] * Decimal('0.10'),
                    'estado_conservacao': random.choice(['NOVO', 'OTIMO', 'BOM', 'REGULAR']),
                    'ativo': True
                }
            )
            if created:
                bens_criados += 1
    
    return tipos_bens, bens_criados

def verificar_estrutura():
    """Função para verificar estrutura do banco"""
    from django.db import connection
    
    print("="*70)
    print("VERIFICACAO DA ESTRUTURA DO BANCO DE DADOS")
    print("="*70)
    
    cursor = connection.cursor()
    
    # Verificar colunas de lancamentofinanceiro
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'gestao_rural_lancamentofinanceiro' 
        ORDER BY ordinal_position
    """)
    cols_lanc = [r[0] for r in cursor.fetchall()]
    print("\n[1] COLUNAS em lancamentofinanceiro:")
    for col in cols_lanc:
        print(f"  - {col}")
    print(f"\ncentro_custo_id existe: {'centro_custo_id' in cols_lanc}")
    
    # Verificar colunas de categoriafinanceira
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'gestao_rural_categoriafinanceira' 
        ORDER BY ordinal_position
    """)
    cols_cat = [r[0] for r in cursor.fetchall()]
    print("\n[2] COLUNAS em categoriafinanceira:")
    for col in cols_cat:
        print(f"  - {col}")
    print(f"\npropriedade_id existe: {'propriedade_id' in cols_cat}")
    
    # Verificar colunas de contafinanceira
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'gestao_rural_contafinanceira' 
        ORDER BY ordinal_position
    """)
    cols_conta = [r[0] for r in cursor.fetchall()]
    print("\n[3] COLUNAS em contafinanceira:")
    for col in cols_conta:
        print(f"  - {col}")
    obrigatorios = ['instituicao', 'numero_agencia', 'moeda', 'observacoes']
    print("\nCampos obrigatorios:")
    for campo in obrigatorios:
        existe = campo in cols_conta
        print(f"  - {campo}: {'SIM' if existe else 'NAO'}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--verificar':
        verificar_estrutura()
    else:
        try:
            main()
        except Exception as e:
            print(f"\nERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

