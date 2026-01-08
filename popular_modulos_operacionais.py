#!/usr/bin/env python
"""
Script para popular dados realistas dos módulos operacionais faltantes
- Funcionários e Folha de Pagamento
- Pastagens e Rotação
- Cochos e Controle
- Setores da Propriedade
- Suplementação
- Combustível
- Equipamentos
- Empreiteiros
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
from gestao_rural.models import Propriedade
from gestao_rural.models_funcionarios import Funcionario, FolhaPagamento, Holerite, PontoFuncionario
from gestao_rural.models_controles_operacionais import Pastagem, Cocho, ControleCocho, RotacaoPastagem
from gestao_rural.models_operacional import (
    TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
    EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
    Empreiteiro, ServicoEmpreiteiro, Equipamento, ManutencaoEquipamento,
    TipoEquipamento
)
from gestao_rural.models_compras_financeiro import SetorPropriedade

User = get_user_model()

def main():
    print("="*70)
    print("POPULANDO MODULOS OPERACIONAIS - MONPEC AGROPECUARIA LTDA")
    print("="*70)
    
    # Buscar produtor e propriedade
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
    
    print(f"\nProdutor: {produtor.nome}")
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Usuario: {usuario.username}\n")
    
    # 1. Criar setores da propriedade
    print("[1/8] Criando setores da propriedade...")
    setores = criar_setores(propriedade)
    print(f"OK: {len(setores)} setores criados\n")
    
    # 2. Criar funcionários
    print("[2/8] Criando funcionarios...")
    funcionarios = criar_funcionarios(propriedade, setores)
    print(f"OK: {len(funcionarios)} funcionarios criados\n")
    
    # 3. Criar folhas de pagamento
    print("[3/8] Criando folhas de pagamento...")
    folhas_criadas = criar_folhas_pagamento(propriedade, funcionarios)
    print(f"OK: {folhas_criadas} folhas criadas\n")
    
    # 4. Criar pastagens
    print("[4/8] Criando pastagens...")
    pastagens = criar_pastagens(propriedade)
    print(f"OK: {len(pastagens)} pastagens criadas\n")
    
    # 5. Criar cochos
    print("[5/8] Criando cochos...")
    cochos = criar_cochos(propriedade, pastagens)
    print(f"OK: {len(cochos)} cochos criados\n")
    
    # 6. Criar estoques e suplementação
    print("[6/8] Criando estoques e suplementacao...")
    estoques, compras, distribuicoes = criar_suplementacao(propriedade, usuario)
    print(f"OK: {len(estoques)} estoques, {compras} compras, {distribuicoes} distribuicoes criadas\n")
    
    # 7. Criar tanques e combustível
    print("[7/8] Criando tanques e controle de combustivel...")
    tanques, abastecimentos, consumos = criar_combustivel(propriedade, usuario)
    print(f"OK: {len(tanques)} tanques, {abastecimentos} abastecimentos, {consumos} consumos criados\n")
    
    # 8. Criar equipamentos e empreiteiros
    print("[8/8] Criando equipamentos e empreiteiros...")
    equipamentos, manutencoes, empreiteiros, servicos = criar_equipamentos_empreiteiros(propriedade, usuario)
    print(f"OK: {len(equipamentos)} equipamentos, {manutencoes} manutencoes, {len(empreiteiros)} empreiteiros, {servicos} servicos criados\n")
    
    # Resumo final
    print("="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Setores: {SetorPropriedade.objects.filter(propriedade=propriedade).count()}")
    print(f"Funcionarios: {Funcionario.objects.filter(propriedade=propriedade).count()}")
    print(f"Folhas de Pagamento: {FolhaPagamento.objects.filter(propriedade=propriedade).count()}")
    print(f"Pastagens: {Pastagem.objects.filter(propriedade=propriedade).count()}")
    print(f"Cochos: {Cocho.objects.filter(propriedade=propriedade).count()}")
    print(f"Estoques Suplementacao: {EstoqueSuplementacao.objects.filter(propriedade=propriedade).count()}")
    print(f"Tanques Combustivel: {TanqueCombustivel.objects.filter(propriedade=propriedade).count()}")
    print(f"Equipamentos: {Equipamento.objects.filter(propriedade=propriedade).count()}")
    print(f"Empreiteiros: {Empreiteiro.objects.filter(propriedade=propriedade).count()}")
    print("="*70)
    print("\nOK: DADOS POPULADOS COM SUCESSO!")

def criar_setores(propriedade):
    """Cria setores da propriedade"""
    setores_data = [
        'Administração',
        'Pecuária',
        'Manutenção',
        'Pastagens',
    ]
    
    setores = []
    for nome_setor in setores_data:
        setor, created = SetorPropriedade.objects.get_or_create(
            propriedade=propriedade,
            nome=nome_setor
        )
        setores.append(setor)
    
    return setores

def criar_funcionarios(propriedade, setores):
    """Cria funcionários realistas"""
    funcionarios_data = [
        {
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            'cargo': 'Gerente de Fazenda',
            'salario': Decimal('8000.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=1825),  # 5 anos atrás
        },
        {
            'nome': 'Maria Santos',
            'cpf': '234.567.890-11',
            'cargo': 'Veterinária',
            'salario': Decimal('6500.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=1095),  # 3 anos atrás
        },
        {
            'nome': 'Pedro Oliveira',
            'cpf': '345.678.901-22',
            'cargo': 'Capataz',
            'salario': Decimal('4500.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=1460),  # 4 anos atrás
        },
        {
            'nome': 'Carlos Souza',
            'cpf': '456.789.012-33',
            'cargo': 'Vaqueiro',
            'salario': Decimal('2500.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=730),  # 2 anos atrás
        },
        {
            'nome': 'Antonio Costa',
            'cpf': '567.890.123-44',
            'cargo': 'Vaqueiro',
            'salario': Decimal('2500.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=365),  # 1 ano atrás
        },
        {
            'nome': 'Roberto Alves',
            'cpf': '678.901.234-55',
            'cargo': 'Mecânico',
            'salario': Decimal('3500.00'),
            'tipo_contrato': 'CLT',
            'data_admissao': date.today() - timedelta(days=545),  # 1.5 anos atrás
        },
    ]
    
    funcionarios = []
    for func_data in funcionarios_data:
        funcionario, created = Funcionario.objects.get_or_create(
            cpf=func_data['cpf'],
            defaults={
                'propriedade': propriedade,
                'nome': func_data['nome'],
                'cargo': func_data['cargo'],
                'salario_base': func_data['salario'],
                'tipo_contrato': func_data['tipo_contrato'],
                'data_admissao': func_data['data_admissao'],
                'situacao': 'ATIVO',
                'sexo': random.choice(['M', 'F']),
                'telefone': f'(67) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'jornada_trabalho': 44
            }
        )
        funcionarios.append(funcionario)
    
    return funcionarios

def criar_folhas_pagamento(propriedade, funcionarios):
    """Cria folhas de pagamento dos últimos 12 meses"""
    folhas_criadas = 0
    
    for mes in range(12, 0, -1):
        data_base = date.today() - timedelta(days=30 * mes)
        competencia = data_base.strftime('%m/%Y')
        data_vencimento = date(data_base.year, data_base.month, 5)  # Dia 5 de cada mês
        
        folha, created = FolhaPagamento.objects.get_or_create(
            propriedade=propriedade,
            competencia=competencia,
            defaults={
                'data_vencimento': data_vencimento,
                'status': 'PAGA' if mes < 3 else 'FECHADA',
                'total_proventos': sum([f.salario_base for f in funcionarios]),
                'total_descontos': sum([f.salario_base for f in funcionarios]) * Decimal('0.15'),  # 15% de descontos
                'total_liquido': sum([f.salario_base for f in funcionarios]) * Decimal('0.85')
            }
        )
        
        if created:
            folhas_criadas += 1
            
            # Criar holerites para cada funcionário
            for funcionario in funcionarios:
                Holerite.objects.get_or_create(
                    folha_pagamento=folha,
                    funcionario=funcionario,
                    defaults={
                        'salario_base': funcionario.salario_base,
                        'total_proventos': funcionario.salario_base,
                        'total_descontos': funcionario.salario_base * Decimal('0.15'),
                        'valor_liquido': funcionario.salario_base * Decimal('0.85'),
                        'dias_trabalhados': 30
                    }
                )
    
    return folhas_criadas

def criar_pastagens(propriedade):
    """Cria pastagens/piquetes"""
    pastagens_data = [
        {'nome': 'Piquete 1 - Braquiária', 'tipo': 'BRACHIARIA', 'area': Decimal('150.00'), 'capacidade': Decimal('2.5')},
        {'nome': 'Piquete 2 - Braquiária', 'tipo': 'BRACHIARIA', 'area': Decimal('180.00'), 'capacidade': Decimal('2.5')},
        {'nome': 'Piquete 3 - Panicum', 'tipo': 'PANICUM', 'area': Decimal('200.00'), 'capacidade': Decimal('3.0')},
        {'nome': 'Piquete 4 - Braquiária', 'tipo': 'BRACHIARIA', 'area': Decimal('170.00'), 'capacidade': Decimal('2.5')},
        {'nome': 'Piquete 5 - Cynodon', 'tipo': 'CYNODON', 'area': Decimal('120.00'), 'capacidade': Decimal('4.0')},
        {'nome': 'Piquete 6 - Braquiária', 'tipo': 'BRACHIARIA', 'area': Decimal('160.00'), 'capacidade': Decimal('2.5')},
        {'nome': 'Piquete 7 - Urochloa', 'tipo': 'UROCHLOA', 'area': Decimal('190.00'), 'capacidade': Decimal('2.8')},
        {'nome': 'Piquete 8 - Braquiária', 'tipo': 'BRACHIARIA', 'area': Decimal('140.00'), 'capacidade': Decimal('2.5')},
    ]
    
    pastagens = []
    for past_data in pastagens_data:
        pastagem, created = Pastagem.objects.get_or_create(
            propriedade=propriedade,
            nome=past_data['nome'],
            defaults={
                'tipo_pastagem': past_data['tipo'],
                'area_ha': past_data['area'],
                'capacidade_suporte': past_data['capacidade'],
                'status': random.choice(['EM_USO', 'EM_USO', 'EM_USO', 'DESCANSO']),  # 75% em uso
                'data_plantio': date.today() - timedelta(days=random.randint(365, 1825))
            }
        )
        pastagens.append(pastagem)
    
    return pastagens

def criar_cochos(propriedade, pastagens):
    """Cria cochos nas pastagens"""
    cochos = []
    
    tipos_cocho = ['SAL', 'RACAO', 'AGUA', 'MISTO']
    
    for pastagem in pastagens:
        # Criar 2-3 cochos por pastagem
        num_cochos = random.randint(2, 3)
        for i in range(num_cochos):
            tipo = random.choice(tipos_cocho)
            capacidade = Decimal(str(random.randint(50, 500))) if tipo != 'AGUA' else Decimal(str(random.randint(1000, 5000)))
            
            cocho, created = Cocho.objects.get_or_create(
                propriedade=propriedade,
                pastagem=pastagem,
                nome=f'{pastagem.nome} - Cocho {i+1} ({tipo})',
                defaults={
                    'tipo_cocho': tipo,
                    'capacidade': capacidade,
                    'unidade_capacidade': 'KG' if tipo != 'AGUA' else 'L',
                    'status': 'ATIVO'
                }
            )
            if created:
                cochos.append(cocho)
    
    return cochos

def criar_suplementacao(propriedade, usuario):
    """Cria estoques, compras e distribuições de suplementação"""
    estoques_data = [
        {'tipo': 'Sal Mineralizado', 'unidade': 'SC', 'quantidade': Decimal('50.00')},
        {'tipo': 'Ração Concentrada', 'unidade': 'TON', 'quantidade': Decimal('10.00')},
        {'tipo': 'Suplemento Proteinado', 'unidade': 'SC', 'quantidade': Decimal('30.00')},
    ]
    
    estoques = []
    for estoque_data in estoques_data:
        estoque, created = EstoqueSuplementacao.objects.get_or_create(
            propriedade=propriedade,
            tipo_suplemento=estoque_data['tipo'],
            defaults={
                'unidade_medida': estoque_data['unidade'],
                'quantidade_atual': estoque_data['quantidade'],
                'quantidade_minima': estoque_data['quantidade'] * Decimal('0.3')
            }
        )
        estoques.append(estoque)
    
    # Criar compras de suplementação
    compras_criadas = 0
    for mes in range(12, 0, -1):
        data_compra = date.today() - timedelta(days=30 * mes)
        estoque = random.choice(estoques)
        
        quantidade = Decimal(str(random.randint(10, 50)))
        preco_unitario = Decimal(str(random.randint(40, 100)))
        
        compra, created = CompraSuplementacao.objects.get_or_create(
            estoque=estoque,
            data=data_compra,
            numero_nota_fiscal=f'NF-{random.randint(100000, 999999)}',
            defaults={
                'fornecedor': 'Nutripec Ração e Suplementos Ltda',
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
                'valor_total': quantidade * preco_unitario,
                'responsavel': usuario
            }
        )
        if created:
            compras_criadas += 1
    
    # Criar distribuições
    distribuicoes_criadas = 0
    for mes in range(6, 0, -1):  # Últimos 6 meses
        data_dist = date.today() - timedelta(days=30 * mes)
        estoque = random.choice(estoques)
        
        quantidade = Decimal(str(random.randint(5, 20)))
        
        from gestao_rural.models_operacional import DistribuicaoSuplementacao
        valor_unitario = estoque.valor_unitario_medio or Decimal('50.00')
        numero_animais = random.randint(50, 200)
        pastagem_nome = random.choice(['Piquete 1', 'Piquete 2', 'Piquete 3', 'Curral'])
        
        distribuicao, created = DistribuicaoSuplementacao.objects.get_or_create(
            estoque=estoque,
            data=data_dist,
            pastagem=pastagem_nome,
            defaults={
                'quantidade': quantidade,
                'numero_animais': numero_animais,
                'valor_unitario': valor_unitario,
                'valor_total': quantidade * valor_unitario,
                'observacoes': f'Distribuicao em {pastagem_nome}',
                'responsavel': usuario
            }
        )
        if created:
            distribuicoes_criadas += 1
    
    return estoques, compras_criadas, distribuicoes_criadas

def criar_combustivel(propriedade, usuario):
    """Cria tanques, abastecimentos e consumos de combustível"""
    tanques_data = [
        {'nome': 'Tanque Principal', 'capacidade': Decimal('5000.00'), 'estoque': Decimal('3000.00')},
        {'nome': 'Tanque Secundário', 'capacidade': Decimal('3000.00'), 'estoque': Decimal('1500.00')},
    ]
    
    tanques = []
    for tanque_data in tanques_data:
        tanque, created = TanqueCombustivel.objects.get_or_create(
            propriedade=propriedade,
            nome=tanque_data['nome'],
            defaults={
                'capacidade_litros': tanque_data['capacidade'],
                'estoque_atual': tanque_data['estoque'],
                'estoque_minimo': tanque_data['capacidade'] * Decimal('0.2'),
                'localizacao': 'Pátio Principal'
            }
        )
        tanques.append(tanque)
    
    # Criar abastecimentos
    abastecimentos_criados = 0
    for mes in range(12, 0, -1):
        data_abast = date.today() - timedelta(days=30 * mes)
        tanque = random.choice(tanques)
        
        quantidade = Decimal(str(random.randint(500, 2000)))
        preco_unitario = Decimal('5.80')  # Preço do diesel
        
        abastecimento, created = AbastecimentoCombustivel.objects.get_or_create(
            propriedade=propriedade,
            tanque=tanque,
            data=data_abast,
            numero_nota_fiscal=f'NF-{random.randint(100000, 999999)}',
            defaults={
                'tipo': 'COMPRA',
                'fornecedor': 'Posto Combustíveis Rural',
                'quantidade_litros': quantidade,
                'preco_unitario': preco_unitario,
                'valor_total': quantidade * preco_unitario,
                'responsavel': usuario
            }
        )
        if created:
            abastecimentos_criados += 1
    
    # Criar consumos
    consumos_criados = 0
    equipamentos = ['Trator John Deere', 'Caminhão Mercedes', 'Pulverizador', 'Máquina de Feno']
    
    for mes in range(12, 0, -1):
        num_consumos = random.randint(10, 20)
        for _ in range(num_consumos):
            data_consumo = date.today() - timedelta(days=30 * mes + random.randint(0, 29))
            tanque = random.choice(tanques)
            
            quantidade = Decimal(str(random.randint(50, 200)))
            
            consumo, created = ConsumoCombustivel.objects.get_or_create(
                propriedade=propriedade,
                tanque=tanque,
                data=data_consumo,
                tipo_equipamento=random.choice(equipamentos),
                defaults={
                    'quantidade_litros': quantidade,
                    'valor_unitario': Decimal('5.80'),
                    'responsavel': usuario
                }
            )
            if created:
                consumos_criados += 1
    
    return tanques, abastecimentos_criados, consumos_criados

def criar_equipamentos_empreiteiros(propriedade, usuario):
    """Cria equipamentos, manutenções, empreiteiros e serviços"""
    # Criar tipos de equipamentos primeiro
    tipos_equip = {}
    tipos_nomes = ['Trator', 'Pulverizador', 'Caminhão', 'Máquina de Feno']
    for tipo_nome in tipos_nomes:
        tipo, created = TipoEquipamento.objects.get_or_create(nome=tipo_nome)
        tipos_equip[tipo_nome] = tipo
    
    # Equipamentos
    equipamentos_data = [
        {'nome': 'Trator John Deere 6110J', 'tipo': 'Trator', 'marca': 'John Deere', 'ano': 2020},
        {'nome': 'Pulverizador Jacto 600L', 'tipo': 'Pulverizador', 'marca': 'Jacto', 'ano': 2019},
        {'nome': 'Caminhão Mercedes-Benz 1114', 'tipo': 'Caminhão', 'marca': 'Mercedes-Benz', 'ano': 2018},
    ]
    
    equipamentos = []
    for equip_data in equipamentos_data:
        tipo_equip = tipos_equip.get(equip_data['tipo'])
        if tipo_equip:
            equipamento, created = Equipamento.objects.get_or_create(
                propriedade=propriedade,
                nome=equip_data['nome'],
                defaults={
                    'tipo': tipo_equip,
                    'marca': equip_data['marca'],
                    'ano': equip_data['ano'],
                    'ativo': True,
                    'valor_aquisicao': Decimal(str(random.randint(50000, 500000))),
                    'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825))
                }
            )
            equipamentos.append(equipamento)
    
    # Manutenções
    manutencoes_criadas = 0
    for mes in range(12, 0, -1):
        if random.random() > 0.7:  # 30% de chance por mês
            data_manut = date.today() - timedelta(days=30 * mes)
            equipamento = random.choice(equipamentos)
            
            tipo_manut = random.choice(['PREVENTIVA', 'CORRETIVA'])
            descricao_manut = f'Manutenção {random.choice(["troca de óleo", "revisão geral", "troca de filtros", "ajuste de motor"])}'
            valor_manut = Decimal(str(random.randint(500, 3000)))
            
            manutencao, created = ManutencaoEquipamento.objects.get_or_create(
                propriedade=propriedade,
                equipamento=equipamento,
                data_agendamento=data_manut,
                descricao=descricao_manut,
                defaults={
                    'tipo': tipo_manut,
                    'data_realizacao': data_manut + timedelta(days=random.randint(0, 5)),
                    'valor_pecas': valor_manut * Decimal('0.6'),
                    'valor_mao_obra': valor_manut * Decimal('0.4'),
                    'valor_total': valor_manut,
                    'status': 'CONCLUIDA',
                    'responsavel': usuario
                }
            )
            if created:
                manutencoes_criadas += 1
    
    # Empreiteiros
    empreiteiros_data = [
        {'nome': 'Construções Rurais MS', 'cpf_cnpj': '14.678.901/0001-55', 'especialidade': 'Construção'},
        {'nome': 'Serviços de Cerca Elétrica', 'cpf_cnpj': '15.789.012/0001-66', 'especialidade': 'Cerca Elétrica'},
        {'nome': 'Manutenção de Pastagens', 'cpf_cnpj': '16.890.123/0001-77', 'especialidade': 'Pastagem'},
    ]
    
    empreiteiros = []
    for emp_data in empreiteiros_data:
        empreiteiro, created = Empreiteiro.objects.get_or_create(
            propriedade=propriedade,
            cpf_cnpj=emp_data['cpf_cnpj'],
            defaults={
                'nome': emp_data['nome'],
                'especialidade': emp_data['especialidade'],
                'telefone': f'(67) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'ativo': True
            }
        )
        empreiteiros.append(empreiteiro)
    
    # Serviços de empreiteiros
    servicos_criados = 0
    for mes in range(12, 0, -1):
        if random.random() > 0.6:  # 40% de chance por mês
            data_servico = date.today() - timedelta(days=30 * mes)
            empreiteiro = random.choice(empreiteiros)
            
            valor_servico = Decimal(str(random.randint(2000, 10000)))
            data_fim = data_servico + timedelta(days=random.randint(5, 30)) if random.random() > 0.3 else None
            
            servico, created = ServicoEmpreiteiro.objects.get_or_create(
                propriedade=propriedade,
                empreiteiro=empreiteiro,
                descricao=f'Serviço de {empreiteiro.especialidade} - {data_servico.strftime("%m/%Y")}',
                defaults={
                    'data_inicio': data_servico,
                    'data_fim': data_fim,
                    'valor_orcamento': valor_servico,
                    'valor_final': valor_servico if data_fim else None,
                    'status': random.choice(['CONCLUIDO', 'EM_ANDAMENTO', 'ORCAMENTO']),
                    'responsavel': usuario
                }
            )
            if created:
                servicos_criados += 1
    
    return equipamentos, manutencoes_criadas, empreiteiros, servicos_criados

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

