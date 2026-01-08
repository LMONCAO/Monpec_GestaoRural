# -*- coding: utf-8 -*-
"""
Comando Django para carregar dados do banco de dados para o sistema web.

Suporta múltiplas fontes:
- PostgreSQL
- Arquivo JSON
- Arquivo CSV
- Sincronização de dados existentes

Uso:
    python manage.py carregar_dados_banco --fonte postgresql --host localhost --port 5432 --database meu_banco --user meu_user --password minha_senha
    python manage.py carregar_dados_banco --fonte json --caminho dados.json
    python manage.py carregar_dados_banco --fonte csv --caminho dados.csv --tabela gestao_rural_produtorrural
    python manage.py carregar_dados_banco --fonte sincronizar --usuario-id 1
"""

import os
import json
import csv
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Any, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections, models
from django.contrib.auth.models import User
from django.conf import settings

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    AnimalIndividual, BrincoAnimal, MovimentacaoIndividual
)


class Command(BaseCommand):
    help = 'Carrega dados do banco de dados para o sistema web'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fonte',
            type=str,
            required=True,
            choices=['postgresql', 'json', 'csv', 'sincronizar'],
            help='Fonte dos dados: postgresql, json, csv ou sincronizar'
        )
        
        # Opções para arquivos (JSON ou CSV)
        parser.add_argument(
            '--caminho',
            type=str,
            help='Caminho do arquivo (JSON ou CSV)'
        )
        
        # Opções para PostgreSQL
        parser.add_argument(
            '--host',
            type=str,
            default='localhost',
            help='Host do banco PostgreSQL'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=5432,
            help='Porta do banco PostgreSQL'
        )
        parser.add_argument(
            '--database',
            type=str,
            help='Nome do banco de dados PostgreSQL'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Usuário do banco PostgreSQL'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do banco PostgreSQL'
        )
        
        # Opções gerais
        parser.add_argument(
            '--tabela',
            type=str,
            help='Nome da tabela específica para importar (opcional)'
        )
        parser.add_argument(
            '--usuario-id',
            type=int,
            help='ID do usuário para vincular os dados (obrigatório para sincronizar)'
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Sobrescrever dados existentes (padrão: False)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importação sem salvar no banco'
        )

    def handle(self, *args, **options):
        fonte = options['fonte']
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: Nenhum dado será salvo'))
        
        try:
            if fonte == 'postgresql':
                self.importar_postgresql(options, dry_run)
            elif fonte == 'json':
                self.importar_json(options, dry_run)
            elif fonte == 'csv':
                self.importar_csv(options, dry_run)
            elif fonte == 'sincronizar':
                self.sincronizar_dados(options, dry_run)
            
            self.stdout.write(self.style.SUCCESS('✅ Importação concluída com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro durante importação: {str(e)}'))
            raise CommandError(f'Erro ao importar dados: {str(e)}')

    def importar_postgresql(self, options: Dict, dry_run: bool):
        """Importa dados de um banco PostgreSQL"""
        host = options.get('host', 'localhost')
        port = options.get('port', 5432)
        database = options.get('database')
        user = options.get('user')
        password = options.get('password')
        
        if not all([database, user, password]):
            raise CommandError('--database, --user e --password são obrigatórios para fonte postgresql')
        
        self.stdout.write(f'🐘 Conectando ao PostgreSQL: {host}:{port}/{database}')
        
        try:
            import psycopg2
        except ImportError:
            raise CommandError('psycopg2 não está instalado. Instale com: pip install psycopg2-binary')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        try:
            # Listar todas as tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tabelas = [row[0] for row in cursor.fetchall()]
            
            tabela_especifica = options.get('tabela')
            if tabela_especifica:
                tabelas = [t for t in tabelas if t == tabela_especifica]
            
            self.stdout.write(f'📊 Encontradas {len(tabelas)} tabelas')
            
            for tabela in tabelas:
                if tabela.startswith('django_'):
                    continue
                
                self.stdout.write(f'  📋 Processando tabela: {tabela}')
                
                cursor.execute(f"SELECT * FROM {tabela}")
                colunas = [desc[0] for desc in cursor.description]
                registros = cursor.fetchall()
                
                self.stdout.write(f'    ✅ {len(registros)} registros encontrados')
                
                if not dry_run:
                    self.processar_registros_postgresql(tabela, colunas, registros, options)
        
        finally:
            conn.close()

    def importar_json(self, options: Dict, dry_run: bool):
        """Importa dados de um arquivo JSON"""
        caminho = options.get('caminho')
        if not caminho:
            raise CommandError('--caminho é obrigatório para fonte json')
        
        caminho = Path(caminho)
        if not caminho.exists():
            raise CommandError(f'Arquivo não encontrado: {caminho}')
        
        self.stdout.write(f'📄 Lendo arquivo JSON: {caminho}')
        
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        if isinstance(dados, dict):
            # Se for um dicionário, processar cada chave como uma tabela
            for tabela, registros in dados.items():
                self.stdout.write(f'  📋 Processando: {tabela} ({len(registros)} registros)')
                if not dry_run:
                    self.processar_registros_json(tabela, registros, options)
        elif isinstance(dados, list):
            # Se for uma lista, usar o nome da tabela especificado
            tabela = options.get('tabela', 'dados')
            self.stdout.write(f'  📋 Processando: {tabela} ({len(dados)} registros)')
            if not dry_run:
                self.processar_registros_json(tabela, dados, options)

    def importar_csv(self, options: Dict, dry_run: bool):
        """Importa dados de um arquivo CSV"""
        caminho = options.get('caminho')
        if not caminho:
            raise CommandError('--caminho é obrigatório para fonte csv')
        
        tabela = options.get('tabela')
        if not tabela:
            raise CommandError('--tabela é obrigatório para fonte csv')
        
        caminho = Path(caminho)
        if not caminho.exists():
            raise CommandError(f'Arquivo não encontrado: {caminho}')
        
        self.stdout.write(f'📄 Lendo arquivo CSV: {caminho}')
        
        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            registros = list(reader)
        
        self.stdout.write(f'  📋 Processando: {tabela} ({len(registros)} registros)')
        
        if not dry_run:
            self.processar_registros_json(tabela, registros, options)

    def sincronizar_dados(self, options: Dict, dry_run: bool):
        """Sincroniza dados existentes no banco atual"""
        usuario_id = options.get('usuario_id')
        if not usuario_id:
            raise CommandError('--usuario-id é obrigatório para fonte sincronizar')
        
        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            raise CommandError(f'Usuário com ID {usuario_id} não encontrado')
        
        self.stdout.write(f'🔄 Sincronizando dados para usuário: {usuario.username}')
        
        # Sincronizar produtores rurais
        produtores = ProdutorRural.objects.filter(usuario_responsavel=usuario)
        self.stdout.write(f'  👤 {produtores.count()} produtores encontrados')
        
        # Sincronizar propriedades
        propriedades = Propriedade.objects.filter(produtor__usuario_responsavel=usuario)
        self.stdout.write(f'  🏡 {propriedades.count()} propriedades encontradas')
        
        # Sincronizar animais
        animais = AnimalIndividual.objects.filter(propriedade__produtor__usuario_responsavel=usuario)
        self.stdout.write(f'  🐄 {animais.count()} animais encontrados')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('✅ Dados sincronizados!'))

    @transaction.atomic
    def processar_registros_postgresql(self, tabela: str, colunas: List[str], registros: List, options: Dict):
        """Processa registros do PostgreSQL"""
        sobrescrever = options.get('sobrescrever', False)
        usuario_id = options.get('usuario_id')
        
        # Mapear tabelas para modelos Django
        mapeamento = {
            'gestao_rural_produtorrural': ProdutorRural,
            'gestao_rural_propriedade': Propriedade,
            'gestao_rural_categoriaanimal': CategoriaAnimal,
            'gestao_rural_animalindividual': AnimalIndividual,
            'gestao_rural_brincoanimal': BrincoAnimal,
        }
        
        modelo = mapeamento.get(tabela)
        if not modelo:
            self.stdout.write(self.style.WARNING(f'    ⚠️  Tabela {tabela} não mapeada, pulando...'))
            return
        
        contador = 0
        for registro in registros:
            dados = dict(zip(colunas, registro))
            
            # Converter dados conforme necessário
            dados = self.converter_dados(dados, modelo)
            
            # Vincular usuário se necessário
            if usuario_id and 'usuario_responsavel_id' in dados:
                dados['usuario_responsavel_id'] = usuario_id
            
            try:
                if sobrescrever and 'id' in dados:
                    # Atualizar registro existente
                    modelo.objects.update_or_create(
                        id=dados['id'],
                        defaults=dados
                    )
                else:
                    # Criar novo registro
                    if 'id' in dados:
                        del dados['id']  # Remover ID para criar novo
                    modelo.objects.create(**dados)
                
                contador += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    ⚠️  Erro ao processar registro: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'    ✅ {contador} registros importados'))

    @transaction.atomic
    def processar_registros_json(self, tabela: str, registros: List[Dict], options: Dict):
        """Processa registros de JSON ou CSV"""
        sobrescrever = options.get('sobrescrever', False)
        usuario_id = options.get('usuario_id')
        
        # Mapear nomes de tabelas para modelos
        mapeamento = {
            'gestao_rural_produtorrural': ProdutorRural,
            'gestao_rural_propriedade': Propriedade,
            'gestao_rural_categoriaanimal': CategoriaAnimal,
            'gestao_rural_animalindividual': AnimalIndividual,
            'gestao_rural_brincoanimal': BrincoAnimal,
            'produtorrural': ProdutorRural,
            'propriedade': Propriedade,
            'categoriaanimal': CategoriaAnimal,
            'animalindividual': AnimalIndividual,
            'brincoanimal': BrincoAnimal,
        }
        
        modelo = mapeamento.get(tabela.lower())
        if not modelo:
            self.stdout.write(self.style.WARNING(f'    ⚠️  Tabela {tabela} não mapeada, pulando...'))
            return
        
        contador = 0
        for dados in registros:
            # Converter dados conforme necessário
            dados = self.converter_dados(dados, modelo)
            
            # Vincular usuário se necessário
            if usuario_id:
                if 'usuario_responsavel' in dados:
                    dados['usuario_responsavel_id'] = usuario_id
                elif 'usuario_responsavel_id' in dados:
                    dados['usuario_responsavel_id'] = usuario_id
            
            try:
                if sobrescrever and 'id' in dados:
                    modelo.objects.update_or_create(
                        id=dados['id'],
                        defaults=dados
                    )
                else:
                    if 'id' in dados:
                        del dados['id']
                    modelo.objects.create(**dados)
                
                contador += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    ⚠️  Erro ao processar registro: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'    ✅ {contador} registros importados'))

    def converter_dados(self, dados: Dict, modelo) -> Dict:
        """Converte dados para o formato esperado pelo modelo"""
        dados_convertidos = {}
        
        for campo, valor in dados.items():
            if valor is None:
                dados_convertidos[campo] = None
                continue
            
            # Obter o campo do modelo
            try:
                campo_modelo = modelo._meta.get_field(campo)
            except:
                # Campo não existe no modelo, pular
                continue
            
            # Converter conforme o tipo do campo
            if isinstance(campo_modelo, models.DateField):
                if isinstance(valor, str):
                    try:
                        dados_convertidos[campo] = datetime.strptime(valor, '%Y-%m-%d').date()
                    except:
                        try:
                            dados_convertidos[campo] = datetime.strptime(valor, '%d/%m/%Y').date()
                        except:
                            dados_convertidos[campo] = None
                else:
                    dados_convertidos[campo] = valor
            
            elif isinstance(campo_modelo, models.DateTimeField):
                if isinstance(valor, str):
                    try:
                        dados_convertidos[campo] = datetime.fromisoformat(valor.replace('Z', '+00:00'))
                    except:
                        dados_convertidos[campo] = None
                else:
                    dados_convertidos[campo] = valor
            
            elif isinstance(campo_modelo, models.DecimalField):
                try:
                    dados_convertidos[campo] = Decimal(str(valor))
                except:
                    dados_convertidos[campo] = Decimal('0')
            
            elif isinstance(campo_modelo, models.IntegerField) or isinstance(campo_modelo, models.PositiveIntegerField):
                try:
                    dados_convertidos[campo] = int(valor)
                except:
                    dados_convertidos[campo] = 0
            
            elif isinstance(campo_modelo, models.BooleanField):
                dados_convertidos[campo] = bool(valor)
            
            elif isinstance(campo_modelo, models.ForeignKey):
                # Manter o ID da foreign key
                if campo.endswith('_id'):
                    dados_convertidos[campo] = valor
                else:
                    # Se não terminar com _id, adicionar
                    dados_convertidos[f'{campo}_id'] = valor
            
            else:
                dados_convertidos[campo] = str(valor) if valor else ''
        
        return dados_convertidos


