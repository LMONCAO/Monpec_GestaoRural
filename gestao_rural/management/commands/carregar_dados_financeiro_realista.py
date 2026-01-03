# -*- coding: utf-8 -*-
"""
Comando para carregar dados financeiros realistas com variação mensal,
fornecedores, notas fiscais e fluxo de caixa controlado.
"""
import re
from decimal import Decimal
from datetime import date, timedelta
from random import randint, choice, uniform, random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro
)
from gestao_rural.models_compras_financeiro import Fornecedor, NotaFiscal

# Importar dados reais de fornecedores do arquivo cadastrar_fornecedores_nf.py
try:
    import sys
    import os
    # Adicionar o diretório raiz ao path para importar o módulo
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, base_dir)
    from cadastrar_fornecedores_nf import dados_nf as DADOS_NF_FORNECEDORES
except ImportError:
    # Fallback: usar string vazia se não conseguir importar
    DADOS_NF_FORNECEDORES = ""


class Command(BaseCommand):
    help = 'Carrega dados financeiros realistas com fornecedores, notas fiscais e variação mensal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID da propriedade (se não informado, usa a primeira)',
        )
        parser.add_argument(
            '--ano',
            type=int,
            default=timezone.now().year,
            help='Ano para gerar os dados (padrão: ano atual)',
        )
        parser.add_argument(
            '--meses',
            type=int,
            default=12,
            help='Número de meses para gerar (padrão: 12)',
        )
        parser.add_argument(
            '--receita-media',
            type=float,
            default=500000.00,
            help='Receita média mensal em R$ (padrão: 500.000)',
        )
        parser.add_argument(
            '--despesa-media',
            type=float,
            default=450000.00,
            help='Despesa média mensal em R$ (padrão: 450.000)',
        )

    def handle(self, *args, **options):
        propriedade_id = options.get('propriedade_id')
        ano = options.get('ano')
        meses = options.get('meses')
        receita_media = Decimal(str(options.get('receita_media')))
        despesa_media = Decimal(str(options.get('despesa_media')))

        # Buscar propriedade
        if propriedade_id:
            try:
                propriedade = Propriedade.objects.get(pk=propriedade_id)
            except Propriedade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Propriedade {propriedade_id} não encontrada'))
                return
        else:
            propriedade = Propriedade.objects.first()
            if not propriedade:
                self.stdout.write(self.style.ERROR('Nenhuma propriedade encontrada'))
                return

        self.stdout.write(self.style.SUCCESS(f'Carregando dados para: {propriedade.nome_propriedade}'))
        self.stdout.write(f'Ano: {ano} | Meses: {meses} | Receita média: R$ {receita_media:,.2f} | Despesa média: R$ {despesa_media:,.2f}')

        with transaction.atomic():
            # 1. Criar fornecedores
            fornecedores = self._criar_fornecedores(propriedade)
            self.stdout.write(self.style.SUCCESS(f'[OK] {len(fornecedores)} fornecedores criados'))

            # 2. Criar centros de custo
            centros_custo = self._criar_centros_custo(propriedade)
            self.stdout.write(self.style.SUCCESS(f'[OK] {len(centros_custo)} centros de custo criados'))

            # 3. Criar/obter categorias financeiras
            categorias = self._criar_obter_categorias(propriedade)
            self.stdout.write(self.style.SUCCESS(f'[OK] {len(categorias["receitas"]) + len(categorias["despesas"])} categorias preparadas'))

            # 4. Criar/obter contas financeiras
            contas = self._criar_obter_contas(propriedade)
            self.stdout.write(self.style.SUCCESS(f'[OK] {len(contas)} contas financeiras preparadas'))

            # 5. Gerar lançamentos mensais com variação
            saldo_atual = Decimal('100000.00')  # Saldo inicial
            total_receitas = Decimal('0.00')
            total_despesas = Decimal('0.00')
            lancamentos_criados = 0
            notas_criadas = 0

            for mes in range(1, meses + 1):
                data_base = date(ano, mes, 1)
                ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day if mes < 12 else 31

                # Variação mensal: -30% a +20% para receitas, -20% a +30% para despesas
                variacao_receita = uniform(0.70, 1.20)
                variacao_despesa = uniform(0.80, 1.30)

                receita_mes = receita_media * Decimal(str(variacao_receita))
                despesa_mes = despesa_media * Decimal(str(variacao_despesa))

                # Gerar receitas
                receitas_mes = self._gerar_receitas_mes(
                    propriedade, data_base, ultimo_dia, receita_mes,
                    categorias['receitas'], contas
                )
                lancamentos_criados += len(receitas_mes)
                total_receitas += receita_mes

                # Gerar despesas com notas fiscais
                despesas_mes, notas_mes = self._gerar_despesas_mes(
                    propriedade, data_base, ultimo_dia, despesa_mes,
                    categorias['despesas'], contas, fornecedores, centros_custo
                )
                lancamentos_criados += len(despesas_mes)
                notas_criadas += len(notas_mes)
                total_despesas += despesa_mes

                # Atualizar saldo
                saldo_atual = saldo_atual + receita_mes - despesa_mes

                # Garantir que não fique muito negativo (mínimo -50.000)
                if saldo_atual < Decimal('-50000.00'):
                    # Ajustar despesas do próximo mês
                    despesa_media = receita_media * Decimal('0.85')

                self.stdout.write(
                    f'  Mês {mes:02d}/{ano}: '
                    f'Receitas R$ {receita_mes:,.2f} | '
                    f'Despesas R$ {despesa_mes:,.2f} | '
                    f'Saldo R$ {saldo_atual:,.2f}'
                )

            self.stdout.write(self.style.SUCCESS(f'\n[OK] {lancamentos_criados} lancamentos criados'))
            self.stdout.write(self.style.SUCCESS(f'[OK] {notas_criadas} notas fiscais criadas'))
            self.stdout.write(self.style.SUCCESS(f'[OK] Total Receitas: R$ {total_receitas:,.2f}'))
            self.stdout.write(self.style.SUCCESS(f'[OK] Total Despesas: R$ {total_despesas:,.2f}'))
            self.stdout.write(self.style.SUCCESS(f'[OK] Saldo Final: R$ {saldo_atual:,.2f}'))

    def _formatar_cnpj_cpf(self, valor):
        """Formata CNPJ/CPF removendo caracteres especiais e adicionando formatação"""
        if not valor or valor == '000000000':
            return None
        # Remove caracteres não numéricos
        valor_limpo = re.sub(r'\D', '', str(valor))
        if len(valor_limpo) == 11:
            # CPF: 000.000.000-00
            return f"{valor_limpo[:3]}.{valor_limpo[3:6]}.{valor_limpo[6:9]}-{valor_limpo[9:]}"
        elif len(valor_limpo) == 14:
            # CNPJ: 00.000.000/0000-00
            return f"{valor_limpo[:2]}.{valor_limpo[2:5]}.{valor_limpo[5:8]}/{valor_limpo[8:12]}-{valor_limpo[12:]}"
        return valor_limpo

    def _determinar_tipo_fornecedor(self, nome):
        """Determina o tipo de fornecedor baseado no nome"""
        nome_upper = nome.upper()
        
        if any(palavra in nome_upper for palavra in ['RACAO', 'NUTRI', 'ALIMENTO', 'RAÇÃO', 'SUPLEMENTO', 'AGROPECUARIO', 'AGROPECUÁRIO']):
            return 'RACAO'
        elif any(palavra in nome_upper for palavra in ['MEDICAMENTO', 'VETERINARIO', 'VETERINÁRIO', 'VACINA']):
            return 'MEDICAMENTO'
        elif any(palavra in nome_upper for palavra in ['TRATOR', 'EQUIPAMENTO', 'PECA', 'PEÇA', 'MAQUINA', 'MÁQUINA', 'VEICULO', 'VEÍCULO', 'AUTO', 'MOTOR']):
            return 'EQUIPAMENTO'
        elif any(palavra in nome_upper for palavra in ['COMBUSTIVEL', 'COMBUSTÍVEL', 'PETROLEO', 'PETRÓLEO', 'DIESEL', 'GASOLINA', 'DISTRIBUIDORA']):
            return 'COMBUSTIVEL'
        elif any(palavra in nome_upper for palavra in ['CONSTRUCAO', 'CONSTRUÇÃO', 'MATERIAL', 'CONSTRUIR']):
            return 'CONSTRUCAO'
        elif any(palavra in nome_upper for palavra in ['TRANSPORTE', 'FRETE', 'LOGISTICA', 'LOGÍSTICA']):
            return 'TRANSPORTE'
        elif any(palavra in nome_upper for palavra in ['SERVICO', 'SERVIÇO', 'INTERNET', 'TELECOM', 'LEILOES', 'LEILÕES']):
            return 'SERVICO'
        else:
            return 'OUTROS'

    def _processar_linha_fornecedor(self, linha):
        """Processa uma linha de dados e extrai informações do fornecedor"""
        campos = linha.split('\t')
        if len(campos) < 5:
            # Tentar separar por múltiplos espaços
            campos = re.split(r'\s{2,}', linha.strip())
        
        # Estrutura esperada: Chave NF | IE Dest | IE Emit | Razão Social | CNPJ/CPF | Nº NF | Data | UF | Total | Base ICMS | ICMS | Situação
        if len(campos) >= 5:
            try:
                razao_social = campos[3].strip() if len(campos) > 3 else ''
                cnpj_cpf = campos[4].strip() if len(campos) > 4 else ''
                uf = campos[7].strip() if len(campos) > 7 else 'MS'
                
                # Ignorar linhas inválidas
                if not razao_social or not cnpj_cpf or cnpj_cpf == '000000000':
                    return None
                
                return {
                    'nome': razao_social,
                    'cpf_cnpj': self._formatar_cnpj_cpf(cnpj_cpf),
                    'estado': uf,
                    'tipo': self._determinar_tipo_fornecedor(razao_social),
                }
            except (IndexError, ValueError):
                return None
        return None

    def _criar_fornecedores(self, propriedade):
        """Cria fornecedores reais a partir da listagem de notas fiscais."""
        fornecedores_unicos = {}
        
        # Processar linhas dos dados de NF
        linhas = DADOS_NF_FORNECEDORES.strip().split('\n')
        for linha in linhas:
            if not linha.strip():
                continue
            
            dados = self._processar_linha_fornecedor(linha)
            if dados and dados['cpf_cnpj']:
                # Usar CNPJ/CPF como chave única
                cnpj_cpf_limpo = re.sub(r'\D', '', dados['cpf_cnpj'])
                if cnpj_cpf_limpo not in fornecedores_unicos:
                    fornecedores_unicos[cnpj_cpf_limpo] = dados
                else:
                    # Se já existe, atualizar tipo se necessário (priorizar tipos mais específicos)
                    tipo_atual = fornecedores_unicos[cnpj_cpf_limpo]['tipo']
                    tipo_novo = dados['tipo']
                    if tipo_atual == 'OUTROS' and tipo_novo != 'OUTROS':
                        fornecedores_unicos[cnpj_cpf_limpo]['tipo'] = tipo_novo

        fornecedores = []
        for cnpj_cpf_limpo, dados in fornecedores_unicos.items():
            fornecedor, created = Fornecedor.objects.get_or_create(
                cpf_cnpj=dados['cpf_cnpj'],
                defaults={
                    'propriedade': propriedade,
                    'nome': dados['nome'],
                    'tipo': dados['tipo'],
                    'telefone': f'(67) {randint(3000, 9999)}-{randint(1000, 9999)}',
                    'email': f'contato@{dados["nome"].lower().replace(" ", "").replace("/", "")[:30]}.com.br',
                    'cidade': 'Campo Grande',
                    'estado': dados.get('estado', 'MS'),
                }
            )
            fornecedores.append(fornecedor)

        return fornecedores

    def _criar_centros_custo(self, propriedade):
        """Cria centros de custo."""
        centros = [
            {'nome': 'Bovinos de Corte', 'tipo': 'PRODUCAO'},
            {'nome': 'Reprodução', 'tipo': 'PRODUCAO'},
            {'nome': 'Cria', 'tipo': 'PRODUCAO'},
            {'nome': 'Recria', 'tipo': 'PRODUCAO'},
            {'nome': 'Engorda', 'tipo': 'PRODUCAO'},
            {'nome': 'Administração', 'tipo': 'ADMINISTRATIVO'},
            {'nome': 'Manutenção', 'tipo': 'ADMINISTRATIVO'},
        ]

        centros_custo = []
        for dados in centros:
            centro, created = CentroCusto.objects.get_or_create(
                propriedade=propriedade,
                nome=dados['nome'],
                defaults={'tipo': dados['tipo']}
            )
            centros_custo.append(centro)

        return centros_custo

    def _criar_obter_categorias(self, propriedade):
        """Cria ou obtém categorias financeiras."""
        receitas_cat = [
            {'nome': 'Venda de Gado', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
            {'nome': 'Venda de Bezerros', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
            {'nome': 'Venda de Touros', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
            {'nome': 'Renda de Arrendamento', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
        ]

        despesas_cat = [
            {'nome': 'Ração e Suplementos', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Medicamentos e Veterinário', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Combustível', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Mão de Obra', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Manutenção de Equipamentos', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Energia Elétrica', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Telefone e Internet', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Aluguel/Arrendamento', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Impostos e Taxas', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Serviços Terceirizados', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
        ]

        receitas = []
        for dados in receitas_cat:
            cat, created = CategoriaFinanceira.objects.get_or_create(
                propriedade=propriedade,
                nome=dados['nome'],
                defaults={'tipo': dados['tipo']}
            )
            receitas.append(cat)

        despesas = []
        for dados in despesas_cat:
            cat, created = CategoriaFinanceira.objects.get_or_create(
                propriedade=propriedade,
                nome=dados['nome'],
                defaults={'tipo': dados['tipo']}
            )
            despesas.append(cat)

        return {'receitas': receitas, 'despesas': despesas}

    def _criar_obter_contas(self, propriedade):
        """Cria ou obtém contas financeiras."""
        contas_data = [
            {'nome': 'Caixa', 'tipo': ContaFinanceira.TIPO_CAIXA, 'saldo_inicial': Decimal('50000.00')},
            {'nome': 'Banco do Brasil', 'tipo': ContaFinanceira.TIPO_CORRENTE, 'saldo_inicial': Decimal('100000.00')},
            {'nome': 'Poupança', 'tipo': ContaFinanceira.TIPO_POUPANCA, 'saldo_inicial': Decimal('50000.00')},
        ]

        contas = []
        from django.db import connection
        from django.utils import timezone
        
        # Verificar quais colunas existem no banco e quais são NOT NULL
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(gestao_rural_contafinanceira)")
            columns_info = cursor.fetchall()
            # row[1] = nome da coluna, row[3] = NOT NULL (1 = NOT NULL, 0 = nullable), row[4] = default value
            columns = {row[1]: {'notnull': row[3], 'default': row[4]} for row in columns_info}
            tem_instituicao = 'instituicao' in columns
            tem_numero_agencia = 'numero_agencia' in columns
            tem_criado_em = 'criado_em' in columns
            tem_atualizado_em = 'atualizado_em' in columns
            tem_created_at = 'created_at' in columns
            tem_updated_at = 'updated_at' in columns
            tem_ativa = 'ativa' in columns
            tem_data_saldo_inicial = 'data_saldo_inicial' in columns
            tem_moeda = 'moeda' in columns
            
            # Lista de campos NOT NULL que não têm default e não estão na lista principal
            campos_notnull_sem_default = []
            for col_name, col_info in columns.items():
                if col_info['notnull'] and not col_info['default'] and col_name not in [
                    'id', 'propriedade_id', 'nome', 'tipo', 'saldo_inicial', 'banco', 
                    'agencia', 'numero_conta', 'instituicao', 'numero_agencia', 
                    'data_saldo_inicial', 'ativa', 'criado_em', 'atualizado_em', 
                    'created_at', 'updated_at', 'moeda'
                ]:
                    campos_notnull_sem_default.append(col_name)
        
        for dados in contas_data:
            banco_nome = 'Banco do Brasil' if dados['tipo'] != ContaFinanceira.TIPO_CAIXA else ''
            agencia_valor = '0001' if dados['tipo'] != ContaFinanceira.TIPO_CAIXA else ''
            conta_valor = f'{randint(10000, 99999)}-{randint(0, 9)}' if dados['tipo'] != ContaFinanceira.TIPO_CAIXA else ''
            
            # Tentar obter conta existente
            conta = ContaFinanceira.objects.filter(
                propriedade=propriedade,
                nome=dados['nome']
            ).first()
            
            if conta:
                contas.append(conta)
                continue
            
            # Se o banco tem campo instituicao (NOT NULL), sempre usar SQL direto
            if tem_instituicao:
                with connection.cursor() as cursor:
                    # Construir SQL dinamicamente
                    colunas_sql = ['propriedade_id', 'nome', 'tipo', 'saldo_inicial', 'banco', 'agencia', 'numero_conta', 'instituicao']
                    valores_sql = [propriedade.id, dados['nome'], dados['tipo'], str(dados['saldo_inicial']), banco_nome, agencia_valor, conta_valor, banco_nome]
                    
                    if tem_numero_agencia:
                        colunas_sql.append('numero_agencia')
                        valores_sql.append(agencia_valor)
                    
                    if tem_data_saldo_inicial:
                        colunas_sql.append('data_saldo_inicial')
                        valores_sql.append(timezone.now().date())
                    
                    if tem_moeda:
                        colunas_sql.append('moeda')
                        valores_sql.append('BRL')
                    
                    if tem_ativa:
                        colunas_sql.append('ativa')
                        valores_sql.append(1)
                    
                    # Campos de timestamp
                    agora = timezone.now()
                    if tem_criado_em:
                        colunas_sql.append('criado_em')
                        valores_sql.append(agora)
                    elif tem_created_at:
                        colunas_sql.append('created_at')
                        valores_sql.append(agora)
                    
                    if tem_atualizado_em:
                        colunas_sql.append('atualizado_em')
                        valores_sql.append(agora)
                    elif tem_updated_at:
                        colunas_sql.append('updated_at')
                        valores_sql.append(agora)
                    
                    # Adicionar outros campos NOT NULL sem default
                    for campo in campos_notnull_sem_default:
                        if campo not in colunas_sql:
                            colunas_sql.append(campo)
                            if 'data' in campo.lower() or 'date' in campo.lower():
                                valores_sql.append(timezone.now().date())
                            elif 'moeda' in campo.lower():
                                valores_sql.append('BRL')
                            elif campo.lower() in ['ativa', 'ativo', 'active']:
                                valores_sql.append(1)
                            else:
                                valores_sql.append('')
                    
                    # Montar SQL
                    placeholders = ', '.join(['?' for _ in colunas_sql])
                    colunas_str = ', '.join(colunas_sql)
                    sql = f"INSERT INTO gestao_rural_contafinanceira ({colunas_str}) VALUES ({placeholders})"
                    
                    # Executar SQL diretamente - usar _execute para evitar problema de debug
                    # O problema é que o Django tenta formatar o SQL para debug usando %, mas usamos ? placeholders
                    # Vamos usar o método interno do cursor para evitar isso
                    import sqlite3
                    # Converter valores para tipos compatíveis com SQLite
                    valores_sqlite = []
                    for v in valores_sql:
                        if isinstance(v, (date, timezone.datetime)):
                            valores_sqlite.append(v.isoformat() if hasattr(v, 'isoformat') else str(v))
                        else:
                            valores_sqlite.append(v)
                    
                    # Usar execute diretamente no cursor SQLite (bypass Django debug)
                    cursor._execute(sql, tuple(valores_sqlite))
                    conta_id = cursor.lastrowid
                    conta = ContaFinanceira.objects.get(id=conta_id)
            else:
                # Se não tem campo instituicao, usar método normal do Django
                conta_kwargs = {
                    'propriedade': propriedade,
                    'nome': dados['nome'],
                    'tipo': dados['tipo'],
                    'saldo_inicial': dados['saldo_inicial'],
                    'banco': banco_nome,
                    'agencia': agencia_valor,
                    'numero_conta': conta_valor,
                }
                
                if tem_data_saldo_inicial:
                    conta_kwargs['data_saldo_inicial'] = timezone.now().date()
                
                conta = ContaFinanceira.objects.create(**conta_kwargs)
            
            contas.append(conta)

        return contas

    def _gerar_receitas_mes(self, propriedade, data_base, ultimo_dia, total_receita,
                            categorias, contas):
        """Gera receitas do mês."""
        lancamentos = []
        receita_restante = total_receita
        # Aumentar número de receitas: 20-40 por mês (proporcional ao aumento de despesas)
        num_lancamentos = randint(20, 40)

        for i in range(num_lancamentos):
            if i == num_lancamentos - 1:
                valor = receita_restante  # Último lançamento pega o restante
            else:
                # Com mais lançamentos, usar percentuais menores para distribuir melhor
                percentual = uniform(0.01, 0.08)  # 1% a 8% por lançamento
                valor = total_receita * Decimal(str(percentual))
                receita_restante -= valor

            dia = randint(1, ultimo_dia)
            data_competencia = date(data_base.year, data_base.month, dia)
            data_vencimento = data_competencia
            data_quitacao = data_competencia + timedelta(days=randint(0, 5))

            lancamento = LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=choice(categorias),
                conta_destino=choice(contas),
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao=f'Venda de gado - {data_competencia.strftime("%d/%m/%Y")}',
                valor=valor.quantize(Decimal('0.01')),
                data_competencia=data_competencia,
                data_vencimento=data_vencimento,
                data_quitacao=data_quitacao,
                forma_pagamento=choice([
                    LancamentoFinanceiro.FORMA_PIX,
                    LancamentoFinanceiro.FORMA_TRANSFERENCIA,
                    LancamentoFinanceiro.FORMA_DINHEIRO,
                ]),
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            lancamentos.append(lancamento)

        return lancamentos

    def _gerar_despesas_mes(self, propriedade, data_base, ultimo_dia, total_despesa,
                            categorias, contas, fornecedores, centros_custo):
        """Gera despesas do mês com notas fiscais."""
        lancamentos = []
        notas = []
        despesa_restante = total_despesa
        # Aumentar significativamente: 260 a 320 despesas por mês
        num_lancamentos = randint(260, 320)

        # Mapear categorias para fornecedores
        categoria_fornecedor_map = {
            'Ração e Suplementos': ['RACAO'],
            'Medicamentos e Veterinário': ['MEDICAMENTO'],
            'Combustível': ['COMBUSTIVEL'],
            'Serviços Terceirizados': ['SERVICO'],
            'Manutenção de Equipamentos': ['EQUIPAMENTO', 'SERVICO'],
        }

        for i in range(num_lancamentos):
            if i == num_lancamentos - 1:
                valor = despesa_restante
            else:
                # Com mais lançamentos, usar percentuais menores para distribuir melhor
                percentual = uniform(0.001, 0.005)  # 0.1% a 0.5% por lançamento
                valor = total_despesa * Decimal(str(percentual))
                despesa_restante -= valor

            dia = randint(1, ultimo_dia)
            data_competencia = date(data_base.year, data_base.month, dia)
            data_vencimento = data_competencia + timedelta(days=randint(0, 30))
            # TODOS os lançamentos serão quitados (sem pendências)
            data_quitacao = data_vencimento + timedelta(days=randint(0, 10))

            categoria = choice(categorias)
            
            # Escolher fornecedor baseado na categoria
            fornecedor = None
            if categoria.nome in categoria_fornecedor_map:
                tipos_fornecedor = categoria_fornecedor_map[categoria.nome]
                fornecedores_filtrados = [f for f in fornecedores if f.tipo in tipos_fornecedor]
                if fornecedores_filtrados:
                    fornecedor = choice(fornecedores_filtrados)
            
            if not fornecedor:
                fornecedor = choice(fornecedores)

            # Criar nota fiscal (90% das despesas têm nota - mais realista)
            nota = None
            numero_nota = None
            if random() > 0.1:  # 90% de chance de ter nota fiscal
                numero_nota = f'{randint(1000, 9999)}{randint(100000, 999999)}'
                serie = '1'
                chave_acesso = ''.join([str(randint(0, 9)) for _ in range(44)])

                nota = NotaFiscal.objects.create(
                    propriedade=propriedade,
                    fornecedor=fornecedor,
                    tipo='ENTRADA',
                    numero=numero_nota,
                    serie=serie,
                    chave_acesso=chave_acesso,
                    data_emissao=data_competencia,
                    data_entrada=data_competencia,
                    valor_produtos=valor.quantize(Decimal('0.01')),
                    valor_total=valor.quantize(Decimal('0.01')),
                    status='AUTORIZADA',
                )
                notas.append(nota)

            # Criar lançamento financeiro - TODOS QUITADOS (sem pendências)
            lancamento = LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria,
                centro_custo=choice(centros_custo) if random() > 0.3 else None,
                conta_origem=choice(contas),
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'{categoria.nome} - {fornecedor.nome}',
                valor=valor.quantize(Decimal('0.01')),
                data_competencia=data_competencia,
                data_vencimento=data_vencimento,
                data_quitacao=data_quitacao,
                forma_pagamento=choice([
                    LancamentoFinanceiro.FORMA_PIX,
                    LancamentoFinanceiro.FORMA_BOLETO,
                    LancamentoFinanceiro.FORMA_TRANSFERENCIA,
                ]),
                status=LancamentoFinanceiro.STATUS_QUITADO,  # SEMPRE QUITADO
                documento_referencia=f'NF {numero_nota}' if numero_nota else '',
            )
            lancamentos.append(lancamento)

        return lancamentos, notas

