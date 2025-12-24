# -*- coding: utf-8 -*-
"""
Comando para popular dados completos do módulo de Compras
Cria fornecedores, setores, produtos, requisições, cotações, ordens de compra, NF-e, etc.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import uuid

from gestao_rural.models import Propriedade
from gestao_rural.models_compras_financeiro import (
    Fornecedor, SetorPropriedade, OrcamentoCompraMensal,
    RequisicaoCompra, ItemRequisicaoCompra, AprovacaoRequisicaoCompra,
    CotacaoFornecedor, ItemCotacaoFornecedor, ConviteCotacaoFornecedor,
    OrdemCompra, ItemOrdemCompra,
    NotaFiscal, ItemNotaFiscal,
    RecebimentoCompra, ItemRecebimentoCompra,
    EventoFluxoCompra, ContaPagar,
    Produto, CategoriaProduto
)


class Command(BaseCommand):
    help = 'Popula dados completos do módulo de Compras para testar o sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID de uma propriedade específica (opcional)',
        )
        parser.add_argument(
            '--propriedade-nome',
            type=str,
            help='Nome da propriedade (procura por "Favo de Mel" se não especificado)',
        )

    def handle(self, *args, **options):
        propriedade_id = options.get('propriedade_id')
        propriedade_nome = options.get('propriedade_nome') or 'Favo de Mel'

        self.stdout.write(self.style.SUCCESS("Iniciando criacao de dados de compras..."))

        # Buscar propriedade
        if propriedade_id:
            try:
                propriedade = Propriedade.objects.get(id=propriedade_id)
            except Propriedade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Propriedade {propriedade_id} nao encontrada!"))
                return
        else:
            if propriedade_nome:
                propriedade = Propriedade.objects.filter(nome_propriedade__icontains=propriedade_nome).first()
            else:
                propriedade = None
                
            if not propriedade:
                # Tentar qualquer propriedade
                propriedade = Propriedade.objects.first()
                if not propriedade:
                    self.stdout.write(self.style.ERROR("Nenhuma propriedade encontrada!"))
                    return

        self.stdout.write(f"Propriedade selecionada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

        # Buscar ou criar usuário admin
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@monpec.com.br',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not user.check_password('admin123'):
            user.set_password('admin123')
            user.save()

        # Criar todos os dados em uma transação
        with transaction.atomic():
            # 1. Categorias de Produtos
            self.stdout.write("\n[1/12] Criando categorias de produtos...")
            categorias = self._criar_categorias_produtos()

            # 2. Produtos
            self.stdout.write("\n[2/12] Criando produtos...")
            produtos = self._criar_produtos(categorias, user)

            # 3. Fornecedores
            self.stdout.write("\n[3/12] Criando fornecedores...")
            fornecedores = self._criar_fornecedores(propriedade)

            # 4. Setores
            self.stdout.write("\n[4/12] Criando setores da propriedade...")
            setores = self._criar_setores(propriedade, user)

            # 5. Orçamentos Mensais
            self.stdout.write("\n[5/12] Criando orcamentos mensais...")
            self._criar_orcamentos(propriedade, setores, user)

            # 6. Requisições de Compra
            self.stdout.write("\n[6/12] Criando requisicoes de compra...")
            requisicoes = self._criar_requisicoes(propriedade, setores, user, produtos)

            # 7. Cotações
            self.stdout.write("\n[7/12] Criando cotacoes...")
            cotacoes = self._criar_cotacoes(requisicoes, fornecedores, user)

            # 8. Convites de Cotação
            self.stdout.write("\n[8/12] Criando convites de cotacao...")
            self._criar_convites(requisicoes, fornecedores, user)

            # 9. Ordens de Compra
            self.stdout.write("\n[9/12] Criando ordens de compra...")
            ordens = self._criar_ordens_compra(propriedade, requisicoes, fornecedores, setores, user, produtos)

            # 10. Recebimentos
            self.stdout.write("\n[10/12] Criando recebimentos...")
            self._criar_recebimentos(ordens, user)

            # 11. Notas Fiscais
            self.stdout.write("\n[11/12] Criando notas fiscais...")
            self._criar_notas_fiscais(propriedade, ordens, fornecedores, produtos, user)

            # 12. Contas a Pagar
            self.stdout.write("\n[12/12] Criando contas a pagar...")
            self._criar_contas_pagar(propriedade, ordens, fornecedores)

        self.stdout.write(self.style.SUCCESS("\nDados de compras criados com sucesso!"))

    def _criar_categorias_produtos(self):
        """Cria categorias de produtos"""
        categorias_data = [
            {'nome': 'Ração', 'descricao': 'Rações para alimentação animal'},
            {'nome': 'Medicamentos', 'descricao': 'Medicamentos veterinários'},
            {'nome': 'Suplementos', 'descricao': 'Suplementos nutricionais'},
            {'nome': 'Equipamentos', 'descricao': 'Equipamentos e máquinas'},
            {'nome': 'Combustível', 'descricao': 'Combustíveis e lubrificantes'},
            {'nome': 'Insumos Agrícolas', 'descricao': 'Fertilizantes, sementes, etc.'},
            {'nome': 'Material de Construção', 'descricao': 'Materiais para construção'},
            {'nome': 'Outros', 'descricao': 'Outros produtos diversos'},
        ]
        
        categorias = []
        for cat_data in categorias_data:
            categoria, created = CategoriaProduto.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            categorias.append(categoria)
            if created:
                self.stdout.write(f"  [OK] Categoria criada: {categoria.nome}")
        
        return categorias

    def _criar_produtos(self, categorias, user):
        """Cria produtos"""
        produtos_data = [
            # Ração
            {'codigo': 'RAC001', 'descricao': 'Ração Concentrada para Gado', 'categoria': 'Ração', 
             'ncm': '2309.90.00', 'unidade': 'KG', 'preco_custo': Decimal('2.50')},
            {'codigo': 'RAC002', 'descricao': 'Ração Pré-secagem', 'categoria': 'Ração',
             'ncm': '2309.90.00', 'unidade': 'KG', 'preco_custo': Decimal('1.80')},
            {'codigo': 'RAC003', 'descricao': 'Sal Mineralizado', 'categoria': 'Ração',
             'ncm': '2501.00.00', 'unidade': 'KG', 'preco_custo': Decimal('1.20')},
            
            # Medicamentos
            {'codigo': 'MED001', 'descricao': 'Vacina Febre Aftosa', 'categoria': 'Medicamentos',
             'ncm': '3002.20.00', 'unidade': 'UN', 'preco_custo': Decimal('15.00')},
            {'codigo': 'MED002', 'descricao': 'Antibiótico Injetável', 'categoria': 'Medicamentos',
             'ncm': '3004.20.00', 'unidade': 'UN', 'preco_custo': Decimal('45.00')},
            {'codigo': 'MED003', 'descricao': 'Vermífugo', 'categoria': 'Medicamentos',
             'ncm': '3004.20.00', 'unidade': 'UN', 'preco_custo': Decimal('28.00')},
            
            # Suplementos
            {'codigo': 'SUP001', 'descricao': 'Suplemento Mineral', 'categoria': 'Suplementos',
             'ncm': '2309.90.00', 'unidade': 'KG', 'preco_custo': Decimal('3.50')},
            {'codigo': 'SUP002', 'descricao': 'Suplemento Proteico', 'categoria': 'Suplementos',
             'ncm': '2309.90.00', 'unidade': 'KG', 'preco_custo': Decimal('4.20')},
            
            # Equipamentos
            {'codigo': 'EQP001', 'descricao': 'Balança Digital', 'categoria': 'Equipamentos',
             'ncm': '8423.81.00', 'unidade': 'UN', 'preco_custo': Decimal('2500.00')},
            {'codigo': 'EQP002', 'descricao': 'Aplicador de Medicamento', 'categoria': 'Equipamentos',
             'ncm': '9018.31.00', 'unidade': 'UN', 'preco_custo': Decimal('180.00')},
            
            # Combustível
            {'codigo': 'COM001', 'descricao': 'Diesel S10', 'categoria': 'Combustível',
             'ncm': '2710.12.21', 'unidade': 'L', 'preco_custo': Decimal('5.80')},
            
            # Insumos Agrícolas
            {'codigo': 'INS001', 'descricao': 'Fertilizante NPK', 'categoria': 'Insumos Agrícolas',
             'ncm': '3105.20.00', 'unidade': 'KG', 'preco_custo': Decimal('4.50')},
            {'codigo': 'INS002', 'descricao': 'Semente de Milho', 'categoria': 'Insumos Agrícolas',
             'ncm': '1005.90.00', 'unidade': 'KG', 'preco_custo': Decimal('8.50')},
        ]
        
        produtos = []
        for prod_data in produtos_data:
            categoria = next((c for c in categorias if c.nome == prod_data['categoria']), None)
            if not categoria:
                continue
                
            produto, created = Produto.objects.get_or_create(
                codigo=prod_data['codigo'],
                defaults={
                    'descricao': prod_data['descricao'],
                    'categoria': categoria,
                    'ncm': prod_data['ncm'],
                    'unidade_medida': prod_data['unidade'],
                    'preco_custo': prod_data['preco_custo'],
                    'preco_venda': prod_data['preco_custo'] * Decimal('1.15'),  # 15% de margem
                    'origem_mercadoria': '0',
                    'aliquota_icms': Decimal('12.00'),
                    'cfop_entrada': '1102',
                    'cfop_saida_estadual': '5102',
                    'cfop_saida_interestadual': '6102',
                    'usuario_cadastro': user,
                    'ativo': True
                }
            )
            produtos.append(produto)
            if created:
                self.stdout.write(f"  [OK] Produto criado: {produto.codigo} - {produto.descricao}")
        
        return produtos

    def _criar_fornecedores(self, propriedade):
        """Cria fornecedores"""
        fornecedores_data = [
            {
                'nome': 'Agropecuária Campo Verde LTDA',
                'nome_fantasia': 'Campo Verde',
                'cpf_cnpj': '12.345.678/0001-90',
                'tipo': 'RACAO',
                'telefone': '(67) 3388-1234',
                'email': 'contato@campoverde.com.br',
                'endereco': 'Av. Principal, 123',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'cep': '79000-000',
            },
            {
                'nome': 'Farmácia Veterinária Rural S.A.',
                'nome_fantasia': 'FarmVet Rural',
                'cpf_cnpj': '98.765.432/0001-10',
                'tipo': 'MEDICAMENTO',
                'telefone': '(67) 3388-5678',
                'email': 'vendas@farmvet.com.br',
                'endereco': 'Rua dos Animais, 456',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'cep': '79010-000',
            },
            {
                'nome': 'Distribuidora de Insumos Agrícolas MS',
                'nome_fantasia': 'DistriAgro MS',
                'cpf_cnpj': '11.222.333/0001-44',
                'tipo': 'OUTROS',
                'telefone': '(67) 3388-9999',
                'email': 'comercial@distriagro.com.br',
                'endereco': 'Rodovia BR-163, Km 12',
                'cidade': 'Dourados',
                'estado': 'MS',
                'cep': '79800-000',
            },
            {
                'nome': 'Posto Combustível Rodoviário',
                'nome_fantasia': 'Posto Rota',
                'cpf_cnpj': '22.333.444/0001-55',
                'tipo': 'COMBUSTIVEL',
                'telefone': '(67) 3388-7777',
                'email': 'vendas@postorota.com.br',
                'endereco': 'BR-163, Km 25',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'cep': '79020-000',
            },
            {
                'nome': 'Suplementos Nutricionais Brasil',
                'nome_fantasia': 'Suplementos Brasil',
                'cpf_cnpj': '33.444.555/0001-66',
                'tipo': 'RACAO',
                'telefone': '(67) 3388-8888',
                'email': 'vendas@suplementosbrasil.com.br',
                'endereco': 'Av. Industrial, 789',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'cep': '79030-000',
            },
            {
                'nome': 'Equipamentos Rurais MS LTDA',
                'nome_fantasia': 'EquipRural MS',
                'cpf_cnpj': '44.555.666/0001-77',
                'tipo': 'EQUIPAMENTO',
                'telefone': '(67) 3388-6666',
                'email': 'vendas@equiprural.com.br',
                'endereco': 'Rua Comercial, 321',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'cep': '79040-000',
            },
        ]
        
        fornecedores = []
        for forn_data in fornecedores_data:
            fornecedor, created = Fornecedor.objects.get_or_create(
                cpf_cnpj=forn_data['cpf_cnpj'],
                defaults={
                    'propriedade': propriedade,
                    **{k: v for k, v in forn_data.items() if k != 'cpf_cnpj'},
                    'ativo': True,
                    'avaliacao': Decimal(str(random.uniform(3.5, 5.0))).quantize(Decimal('0.01'))
                }
            )
            fornecedores.append(fornecedor)
            if created:
                self.stdout.write(f"  [OK] Fornecedor criado: {fornecedor.nome}")
        
        return fornecedores

    def _criar_setores(self, propriedade, user):
        """Cria setores da propriedade"""
        setores_data = [
            {'nome': 'Pecuária', 'codigo': 'PEC', 'descricao': 'Setor de Pecuária'},
            {'nome': 'Agricultura', 'codigo': 'AGR', 'descricao': 'Setor de Agricultura'},
            {'nome': 'Manutenção', 'codigo': 'MAN', 'descricao': 'Setor de Manutenção'},
            {'nome': 'Administração', 'codigo': 'ADM', 'descricao': 'Setor Administrativo'},
            {'nome': 'Infraestrutura', 'codigo': 'INF', 'descricao': 'Setor de Infraestrutura'},
        ]
        
        setores = []
        for setor_data in setores_data:
            setor, created = SetorPropriedade.objects.get_or_create(
                propriedade=propriedade,
                nome=setor_data['nome'],
                defaults={
                    **setor_data,
                    'responsavel': user,
                    'ativo': True
                }
            )
            setores.append(setor)
            if created:
                self.stdout.write(f"  [OK] Setor criado: {setor.nome}")
        
        return setores

    def _criar_orcamentos(self, propriedade, setores, user):
        """Cria orçamentos mensais"""
        ano_atual = date.today().year
        mes_atual = date.today().month
        
        # Criar orçamentos para os próximos 3 meses
        for mes_offset in range(3):
            mes = (mes_atual + mes_offset - 1) % 12 + 1
            ano = ano_atual if (mes_atual + mes_offset - 1) < 12 else ano_atual + 1
            
            for setor in setores:
                valor_base = Decimal('50000.00') if setor.codigo == 'PEC' else Decimal('30000.00')
                orcamento, created = OrcamentoCompraMensal.objects.get_or_create(
                    propriedade=propriedade,
                    setor=setor,
                    ano=ano,
                    mes=mes,
                    defaults={
                        'valor_limite': valor_base,
                        'limite_extra': Decimal('10000.00'),
                        'criado_por': user,
                        'atualizado_por': user
                    }
                )
                if created:
                    self.stdout.write(f"  [OK] Orcamento criado: {setor.nome} - {mes}/{ano}")

    def _criar_requisicoes(self, propriedade, setores, user, produtos):
        """Cria requisições de compra com diferentes status"""
        status_list = [
            ('RASCUNHO', 1),
            ('ENVIADA', 2),
            ('APROVADA_GERENCIA', 2),
            ('EM_COTACAO', 1),
            ('APROVADA_COMPRAS', 1),
            ('ORDEM_EMITIDA', 1),
            ('CONCLUIDA', 2),
        ]
        
        requisicoes = []
        hoje = date.today()
        
        for status, quantidade in status_list:
            for i in range(quantidade):
                setor = random.choice(setores)
                produtos_requisicao = random.sample(produtos, min(3, len(produtos)))
                
                requisicao = RequisicaoCompra.objects.create(
                    propriedade=propriedade,
                    solicitante=user,
                    status=status,
                    prioridade=random.choice(['BAIXA', 'MEDIA', 'ALTA']),
                    titulo=f'Requisição {status} {i+1} - {setor.nome}',
                    justificativa=f'Requisição para {setor.nome} com produtos necessários para operação normal.',
                    data_necessidade=hoje + timedelta(days=random.randint(7, 30)),
                    setor=setor,
                )
                
                # Criar itens da requisição
                for produto in produtos_requisicao:
                    quantidade_item = Decimal(str(random.randint(10, 100)))
                    valor_unitario = produto.preco_custo or Decimal('10.00')
                    
                    ItemRequisicaoCompra.objects.create(
                        requisicao=requisicao,
                        descricao=produto.descricao,
                        unidade_medida=produto.unidade_medida,
                        quantidade=quantidade_item,
                        valor_estimado_unitario=valor_unitario,
                        fornecedor_preferencial=random.choice(['Campo Verde', 'FarmVet Rural', 'DistriAgro MS']),
                    )
                
                # Criar aprovações baseado no status
                if status in ['APROVADA_GERENCIA', 'EM_COTACAO', 'APROVADA_COMPRAS', 'ORDEM_EMITIDA', 'CONCLUIDA']:
                    AprovacaoRequisicaoCompra.objects.create(
                        requisicao=requisicao,
                        etapa='GERENCIA',
                        decisao='APROVADO',
                        usuario=user,
                        comentario='Aprovado pela gerência',
                        data_decisao=timezone.now() - timedelta(days=random.randint(1, 10))
                    )
                
                if status in ['APROVADA_COMPRAS', 'ORDEM_EMITIDA', 'CONCLUIDA']:
                    AprovacaoRequisicaoCompra.objects.create(
                        requisicao=requisicao,
                        etapa='RESPONSAVEL_COMPRAS',
                        decisao='APROVADO',
                        usuario=user,
                        comentario='Aprovado por compras',
                        data_decisao=timezone.now() - timedelta(days=random.randint(1, 5))
                    )
                
                requisicoes.append(requisicao)
                self.stdout.write(f"  [OK] Requisicao criada: {requisicao.titulo} - {requisicao.get_status_display()}")
        
        return requisicoes

    def _criar_cotacoes(self, requisicoes, fornecedores, user):
        """Cria cotações para requisições aprovadas"""
        cotacoes = []
        requisicoes_para_cotar = [r for r in requisicoes if r.status in ['APROVADA_GERENCIA', 'EM_COTACAO', 'APROVADA_COMPRAS']]
        
        for requisicao in requisicoes_para_cotar[:3]:  # Limitar a 3
            fornecedor = random.choice(fornecedores)
            
            cotacao = CotacaoFornecedor.objects.create(
                requisicao=requisicao,
                fornecedor=fornecedor,
                comprador=user,
                status=random.choice(['EM_ANDAMENTO', 'RECEBIDA', 'SELECIONADA']),
                prazo_entrega_estimado='15 dias',
                validade_proposta=date.today() + timedelta(days=30),
                condicoes_pagamento='30/60 dias',
                valor_frete=Decimal(str(random.randint(200, 800))),
            )
            
            # Criar itens da cotação baseado nos itens da requisição
            total_cotacao = Decimal('0.00')
            for item_req in requisicao.itens.all():
                # Variação de preço entre -5% e +10%
                variacao = Decimal(str(random.uniform(0.95, 1.10)))
                valor_unitario = item_req.valor_estimado_unitario * variacao
                
                item_cot = ItemCotacaoFornecedor.objects.create(
                    cotacao=cotacao,
                    item_requisicao=item_req,
                    descricao=item_req.descricao,
                    unidade_medida=item_req.unidade_medida,
                    quantidade=item_req.quantidade,
                    valor_unitario=valor_unitario,
                )
                total_cotacao += item_cot.valor_total
            
            cotacao.valor_total = total_cotacao + cotacao.valor_frete
            cotacao.save()
            
            cotacoes.append(cotacao)
            self.stdout.write(f"  [OK] Cotacao criada: {fornecedor.nome} - R$ {cotacao.valor_total}")
        
        return cotacoes

    def _criar_convites(self, requisicoes, fornecedores, user):
        """Cria convites de cotação"""
        requisicoes_para_convites = [r for r in requisicoes if r.status in ['APROVADA_GERENCIA', 'EM_COTACAO']]
        
        for requisicao in requisicoes_para_convites[:2]:  # Limitar a 2
            fornecedores_selecionados = random.sample(fornecedores, min(3, len(fornecedores)))
            
            for fornecedor in fornecedores_selecionados:
                convite, created = ConviteCotacaoFornecedor.objects.get_or_create(
                    requisicao=requisicao,
                    fornecedor=fornecedor,
                    defaults={
                        'email_destinatario': fornecedor.email,
                        'status': random.choice(['PENDENTE', 'ENVIADO', 'RESPONDIDO']),
                        'enviado_por': user,
                        'enviado_em': timezone.now() - timedelta(days=random.randint(1, 5)) if random.choice([True, False]) else None,
                        'data_expiracao': timezone.now() + timedelta(days=random.randint(1, 7)),
                    }
                )
                if created:
                    self.stdout.write(f"  [OK] Convite criado: {fornecedor.nome}")

    def _criar_ordens_compra(self, propriedade, requisicoes, fornecedores, setores, user, produtos):
        """Cria ordens de compra"""
        ordens = []
        requisicoes_aprovadas = [r for r in requisicoes if r.status in ['APROVADA_COMPRAS', 'ORDEM_EMITIDA', 'CONCLUIDA']]
        
        hoje = date.today()
        sequencial = 1
        
        for requisicao in requisicoes_aprovadas[:4]:  # Limitar a 4
            fornecedor = random.choice(fornecedores)
            setor = requisicao.setor or random.choice(setores)
            
            numero_ordem = f"OC-{hoje.year}{hoje.month:02d}-{sequencial:04d}"
            sequencial += 1
            
            ordem = OrdemCompra.objects.create(
                propriedade=propriedade,
                requisicao_origem=requisicao,
                fornecedor=fornecedor,
                setor=setor,
                numero_ordem=numero_ordem,
                data_emissao=hoje - timedelta(days=random.randint(1, 15)),
                data_entrega_prevista=hoje + timedelta(days=random.randint(7, 30)),
                status=random.choice(['RASCUNHO', 'APROVADA', 'ENVIADA', 'PARCIAL', 'RECEBIDA']),
                autorizacao_setor_status=random.choice(['PENDENTE', 'AUTORIZADA']),
                condicoes_pagamento='30/60 dias',
                forma_pagamento='Boleto',
                aprovado_por=user if random.choice([True, False]) else None,
                data_aprovacao=timezone.now() - timedelta(days=random.randint(1, 10)) if random.choice([True, False]) else None,
                criado_por=user,
            )
            
            # Criar itens da ordem baseado nos itens da requisição
            valor_produtos = Decimal('0.00')
            for item_req in requisicao.itens.all():
                # Buscar produto correspondente se possível
                produto = next((p for p in produtos if item_req.descricao.lower() in p.descricao.lower()), None)
                
                # Pegar cotação se existir
                cotacao = requisicao.cotacoes.filter(status='SELECIONADA').first()
                if cotacao:
                    item_cot = cotacao.itens.filter(item_requisicao=item_req).first()
                    valor_unitario = item_cot.valor_unitario if item_cot else item_req.valor_estimado_unitario
                else:
                    valor_unitario = item_req.valor_estimado_unitario
                
                item_ordem = ItemOrdemCompra.objects.create(
                    ordem_compra=ordem,
                    descricao=item_req.descricao,
                    codigo_produto=produto.codigo if produto else f"COD-{random.randint(1000, 9999)}",
                    unidade_medida=item_req.unidade_medida,
                    quantidade_solicitada=item_req.quantidade,
                    quantidade_recebida=item_req.quantidade * Decimal(str(random.uniform(0.8, 1.0))) if ordem.status in ['PARCIAL', 'RECEBIDA'] else Decimal('0.00'),
                    valor_unitario=valor_unitario,
                )
                valor_produtos += item_ordem.valor_total
            
            ordem.valor_produtos = valor_produtos
            ordem.valor_frete = Decimal(str(random.randint(200, 800)))
            ordem.save()
            
            # Atualizar status da requisição se necessário
            if ordem.status in ['ENVIADA', 'PARCIAL', 'RECEBIDA']:
                requisicao.status = 'ORDEM_EMITIDA'
                requisicao.ordem_compra = ordem
                requisicao.save()
            
            ordens.append(ordem)
            self.stdout.write(f"  [OK] Ordem criada: {ordem.numero_ordem} - {fornecedor.nome} - R$ {ordem.valor_total}")
        
        return ordens

    def _criar_recebimentos(self, ordens, user):
        """Cria recebimentos para ordens"""
        ordens_para_receber = [o for o in ordens if o.status in ['ENVIADA', 'PARCIAL', 'RECEBIDA']]
        
        for ordem in ordens_para_receber[:2]:  # Limitar a 2
            recebimento = RecebimentoCompra.objects.create(
                ordem_compra=ordem,
                responsavel=user,
                status=random.choice(['PENDENTE', 'RECEBIDO']),
                data_prevista=ordem.data_entrega_prevista,
                data_recebimento=date.today() - timedelta(days=random.randint(1, 5)) if random.choice([True, False]) else None,
                observacoes='Recebimento conforme OC' if random.choice([True, False]) else '',
            )
            
            # Criar itens recebidos
            for item_ordem in ordem.itens.all():
                if item_ordem.quantidade_recebida > 0:
                    ItemRecebimentoCompra.objects.create(
                        recebimento=recebimento,
                        item_ordem=item_ordem,
                        quantidade_recebida=item_ordem.quantidade_recebida,
                        divergencia=random.choice([True, False]) if random.randint(1, 10) == 1 else False,
                        justificativa_divergencia='Quantidade menor que solicitada' if random.choice([True, False]) else None,
                    )
            
            self.stdout.write(f"  [OK] Recebimento criado: OC {ordem.numero_ordem}")

    def _criar_notas_fiscais(self, propriedade, ordens, fornecedores, produtos, user):
        """Cria notas fiscais"""
        ordens_com_nf = [o for o in ordens if o.status in ['RECEBIDA']]
        
        for ordem in ordens_com_nf[:2]:  # Limitar a 2
            # Gerar chave de acesso única (44 dígitos)
            while True:
                chave_acesso = ''.join([str(random.randint(0, 9)) for _ in range(44)])
                if not NotaFiscal.objects.filter(chave_acesso=chave_acesso).exists():
                    break
            numero_nf = random.randint(1000, 9999)
            
            nf = NotaFiscal.objects.create(
                propriedade=propriedade,
                fornecedor=ordem.fornecedor,
                tipo='ENTRADA',
                numero=str(numero_nf),
                serie='1',
                chave_acesso=chave_acesso,
                data_emissao=ordem.data_emissao + timedelta(days=random.randint(1, 5)),
                data_entrada=date.today() - timedelta(days=random.randint(1, 5)),
                valor_produtos=ordem.valor_produtos,
                valor_frete=ordem.valor_frete,
                valor_total=ordem.valor_total,
                status=random.choice(['AUTORIZADA', 'PENDENTE']),
                protocolo_autorizacao=f"12345678901234567890{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
                data_autorizacao=timezone.now() - timedelta(days=random.randint(1, 5)) if random.choice([True, False]) else None,
                importado_por=user,
            )
            
            # Criar itens da NF
            for item_ordem in ordem.itens.all():
                # Buscar produto correspondente
                produto = next((p for p in produtos if item_ordem.descricao.lower() in p.descricao.lower()), None)
                
                ItemNotaFiscal.objects.create(
                    nota_fiscal=nf,
                    produto=produto,
                    codigo_produto=item_ordem.codigo_produto,
                    descricao=item_ordem.descricao,
                    ncm=produto.ncm if produto else '2309.90.00',
                    origem_mercadoria=produto.origem_mercadoria if produto else '0',
                    unidade_medida=item_ordem.unidade_medida,
                    quantidade=item_ordem.quantidade_recebida if item_ordem.quantidade_recebida > 0 else item_ordem.quantidade_solicitada,
                    valor_unitario=item_ordem.valor_unitario,
                )
            
            # Vincular NF à ordem
            ordem.nota_fiscal = nf
            ordem.save()
            
            self.stdout.write(f"  [OK] NF-e criada: {nf.numero} - R$ {nf.valor_total}")

    def _criar_contas_pagar(self, propriedade, ordens, fornecedores):
        """Cria contas a pagar"""
        ordens_com_nf = [o for o in ordens if o.nota_fiscal]
        
        for ordem in ordens_com_nf:
            # Criar 1-2 parcelas
            num_parcelas = random.randint(1, 2)
            valor_parcela = ordem.valor_total / num_parcelas
            
            for parcela in range(num_parcelas):
                vencimento = date.today() + timedelta(days=random.randint(15, 60) + (parcela * 30))
                
                conta = ContaPagar.objects.create(
                    propriedade=propriedade,
                    fornecedor=ordem.fornecedor,
                    ordem_compra=ordem,
                    nota_fiscal=ordem.nota_fiscal,
                    descricao=f"Pagamento OC {ordem.numero_ordem} - Parcela {parcela + 1}/{num_parcelas}",
                    categoria='Compras',
                    valor=valor_parcela,
                    data_vencimento=vencimento,
                    status='PENDENTE' if vencimento > date.today() else 'VENCIDA',
                    forma_pagamento='Boleto',
                )
                
                self.stdout.write(f"  [OK] Conta a pagar criada: R$ {conta.valor} - Venc: {conta.data_vencimento}")

