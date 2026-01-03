# -*- coding: utf-8 -*-
"""
Management command para atualizar preços CEPEA no banco de dados
Permite atualização manual, via CSV ou cálculo automático baseado em fatores
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import csv
import os

from gestao_rural.models import PrecoCEPEA
from gestao_rural.apis_integracao.api_cepea import CEPEAService


class Command(BaseCommand):
    help = 'Atualiza preços CEPEA por estado, ano e categoria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--uf',
            type=str,
            help='UF do estado (ex: SP, MG, MT). Se não informado, atualiza todos os estados.',
        )
        parser.add_argument(
            '--ano',
            type=int,
            help='Ano de referência. Se não informado, usa o ano atual.',
        )
        parser.add_argument(
            '--categoria',
            type=str,
            choices=['BEZERRO', 'BEZERRA', 'GARROTE', 'NOVILHA', 'BOI', 'BOI_MAGRO', 
                     'PRIMIPARA', 'MULTIPARA', 'VACA_DESCARTE', 'TOURO'],
            help='Tipo de categoria. Se não informado, atualiza todas as categorias.',
        )
        parser.add_argument(
            '--preco-medio',
            type=float,
            help='Preço médio em R$/cabeça',
        )
        parser.add_argument(
            '--preco-minimo',
            type=float,
            help='Preço mínimo em R$/cabeça (opcional)',
        )
        parser.add_argument(
            '--preco-maximo',
            type=float,
            help='Preço máximo em R$/cabeça (opcional)',
        )
        parser.add_argument(
            '--csv',
            type=str,
            help='Caminho para arquivo CSV com preços. Formato: UF,Ano,Categoria,PrecoMedio,PrecoMinimo,PrecoMaximo',
        )
        parser.add_argument(
            '--calcular-automatico',
            action='store_true',
            help='Calcula preços automaticamente usando fatores de correção por estado',
        )
        parser.add_argument(
            '--fonte',
            type=str,
            default='CEPEA',
            help='Fonte dos dados (padrão: CEPEA)',
        )
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista todos os preços CEPEA cadastrados',
        )
        parser.add_argument(
            '--anos',
            type=str,
            help='Intervalo de anos (ex: 2022-2026) ou lista separada por vírgula (ex: 2022,2023,2024)',
        )
        parser.add_argument(
            '--atualizar-automatico',
            action='store_true',
            help='Atualiza automaticamente todos os preços desde 2022 até hoje + 5 anos futuros com inflação',
        )
        parser.add_argument(
            '--ano-inicio',
            type=int,
            default=2022,
            help='Ano inicial para atualização automática (padrão: 2022)',
        )
        parser.add_argument(
            '--ano-fim',
            type=int,
            help='Ano final para atualização automática (padrão: ano atual + 5)',
        )
        parser.add_argument(
            '--sem-inflacao-futura',
            action='store_true',
            help='Não aplicar inflação para anos futuros na atualização automática',
        )

    def handle(self, *args, **options):
        service = CEPEAService()
        
        # Listar preços existentes
        if options['listar']:
            self.listar_precos(service)
            return
        
        # Importar de CSV
        if options['csv']:
            self.importar_csv(options['csv'], service, options['fonte'])
            return
        
        # Atualização automática completa (recomendado)
        if options['atualizar_automatico']:
            self.atualizar_automatico_completo(options, service)
            return
        
        # Calcular automaticamente
        if options['calcular_automatico']:
            self.calcular_automatico(options, service)
            return
        
        # Atualização manual individual
        if options['preco_medio']:
            self.atualizar_manual(options, service)
            return
        
        # Se nenhuma opção foi fornecida, mostrar ajuda
        self.stdout.write(self.style.WARNING('Nenhuma ação especificada. Use --help para ver opções.'))
        self.stdout.write('\nExemplos de uso:')
        self.stdout.write(self.style.SUCCESS('  # ATUALIZAÇÃO AUTOMÁTICA (RECOMENDADO):'))
        self.stdout.write('  python manage.py atualizar_precos_cepea --atualizar-automatico')
        self.stdout.write('  python manage.py atualizar_precos_cepea --atualizar-automatico --uf SP')
        self.stdout.write('\n  # Outras opções:')
        self.stdout.write('  python manage.py atualizar_precos_cepea --listar')
        self.stdout.write('  python manage.py atualizar_precos_cepea --uf SP --ano 2024 --categoria BOI --preco-medio 3200.00')
        self.stdout.write('  python manage.py atualizar_precos_cepea --calcular-automatico --uf SP --anos 2022-2026')
        self.stdout.write('  python manage.py atualizar_precos_cepea --csv precos_cepea.csv')

    def listar_precos(self, service):
        """Lista todos os preços CEPEA cadastrados"""
        precos = PrecoCEPEA.objects.all().order_by('-ano', 'uf', 'tipo_categoria')
        
        if not precos.exists():
            self.stdout.write(self.style.WARNING('Nenhum preço CEPEA cadastrado.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal de preços cadastrados: {precos.count()}\n'))
        self.stdout.write(f"{'UF':<4} {'Ano':<6} {'Categoria':<20} {'Preço Médio':<15} {'Fonte':<15} {'Atualizado':<20}")
        self.stdout.write('-' * 100)
        
        for preco in precos:
            self.stdout.write(
                f"{preco.uf:<4} {preco.ano:<6} {preco.get_tipo_categoria_display():<20} "
                f"R$ {preco.preco_medio:>12,.2f} {preco.fonte:<15} {preco.data_atualizacao.strftime('%d/%m/%Y %H:%M'):<20}"
            )

    def atualizar_manual(self, options, service):
        """Atualiza preço manualmente"""
        uf = options.get('uf')
        ano = options.get('ano') or datetime.now().year
        categoria = options.get('categoria')
        preco_medio = Decimal(str(options['preco_medio']))
        preco_minimo = Decimal(str(options.get('preco_minimo') or 0)) if options.get('preco_minimo') else None
        preco_maximo = Decimal(str(options.get('preco_maximo') or 0)) if options.get('preco_maximo') else None
        fonte = options.get('fonte', 'CEPEA')
        
        if not uf:
            self.stdout.write(self.style.ERROR('UF é obrigatório para atualização manual.'))
            return
        
        if not categoria:
            self.stdout.write(self.style.ERROR('Categoria é obrigatória para atualização manual.'))
            return
        
        try:
            preco_cepea = service.salvar_preco_cepea(
                uf=uf,
                ano=ano,
                tipo_categoria=categoria,
                preco_medio=preco_medio,
                preco_minimo=preco_minimo,
                preco_maximo=preco_maximo,
                fonte=fonte
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Preço atualizado: {uf} - {ano} - {categoria} = R$ {preco_medio:,.2f}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao atualizar preço: {e}'))

    def calcular_automatico(self, options, service):
        """Calcula preços automaticamente usando fatores de correção"""
        uf = options.get('uf')
        anos_str = options.get('anos', str(datetime.now().year))
        categoria = options.get('categoria')
        fonte = options.get('fonte', 'CEPEA_CALCULADO')
        
        # Processar anos
        anos = self.processar_anos(anos_str)
        
        # Processar categorias
        if categoria:
            categorias = [categoria]
        else:
            categorias = ['BEZERRO', 'BEZERRA', 'GARROTE', 'NOVILHA', 'BOI', 'BOI_MAGRO', 
                         'PRIMIPARA', 'MULTIPARA', 'VACA_DESCARTE', 'TOURO']
        
        # Processar estados
        if uf:
            estados = [uf.upper()]
        else:
            estados = ['SP', 'MG', 'MT', 'MS', 'GO', 'PR', 'SC', 'RS', 'BA', 'PA', 'RO', 'AC', 
                      'TO', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'ES', 'RJ', 'DF']
        
        total_atualizado = 0
        
        with transaction.atomic():
            for estado in estados:
                for ano in anos:
                    for cat in categorias:
                        try:
                            preco = service._obter_preco_padrao_por_estado(estado, ano, cat)
                            if preco:
                                service.salvar_preco_cepea(
                                    uf=estado,
                                    ano=ano,
                                    tipo_categoria=cat,
                                    preco_medio=preco,
                                    fonte=fonte
                                )
                                total_atualizado += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'Erro ao calcular {estado}-{ano}-{cat}: {e}')
                            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Total de preços calculados e salvos: {total_atualizado}')
        )

    def importar_csv(self, caminho_csv, service, fonte):
        """Importa preços de arquivo CSV"""
        if not os.path.exists(caminho_csv):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {caminho_csv}'))
            return
        
        total_importado = 0
        total_erros = 0
        
        try:
            with open(caminho_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for linha, row in enumerate(reader, start=2):  # linha 1 é cabeçalho
                    try:
                        uf = row.get('UF', '').strip().upper()
                        ano = int(row.get('Ano', '').strip())
                        categoria = row.get('Categoria', '').strip().upper()
                        preco_medio = Decimal(str(row.get('PrecoMedio', '0').strip()))
                        preco_minimo = Decimal(str(row.get('PrecoMinimo', '0').strip())) if row.get('PrecoMinimo') else None
                        preco_maximo = Decimal(str(row.get('PrecoMaximo', '0').strip())) if row.get('PrecoMaximo') else None
                        
                        if preco_minimo and preco_minimo == 0:
                            preco_minimo = None
                        if preco_maximo and preco_maximo == 0:
                            preco_maximo = None
                        
                        service.salvar_preco_cepea(
                            uf=uf,
                            ano=ano,
                            tipo_categoria=categoria,
                            preco_medio=preco_medio,
                            preco_minimo=preco_minimo,
                            preco_maximo=preco_maximo,
                            fonte=fonte
                        )
                        total_importado += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Erro na linha {linha}: {e}')
                        )
                        total_erros += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Importação concluída: {total_importado} preços importados, {total_erros} erros'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler arquivo CSV: {e}'))
            self.stdout.write('\nFormato esperado do CSV:')
            self.stdout.write('UF,Ano,Categoria,PrecoMedio,PrecoMinimo,PrecoMaximo')
            self.stdout.write('SP,2024,BOI,3200.00,3000.00,3400.00')

    def atualizar_automatico_completo(self, options, service):
        """Atualiza automaticamente todos os preços desde 2022 até hoje + anos futuros"""
        uf = options.get('uf')
        ano_inicio = options.get('ano_inicio', 2022)
        ano_fim = options.get('ano_fim')
        aplicar_inflacao = not options.get('sem_inflacao_futura', False)
        
        self.stdout.write(self.style.SUCCESS('\n>>> Iniciando atualizacao automatica de precos CEPEA...\n'))
        
        if uf:
            self.stdout.write(f'Estado: {uf}')
        else:
            self.stdout.write('Estados: Todos os estados brasileiros')
        
        self.stdout.write(f'Ano inicial: {ano_inicio}')
        if ano_fim:
            self.stdout.write(f'Ano final: {ano_fim}')
        else:
            from datetime import date
            ano_atual = date.today().year
            ano_fim_calc = ano_atual + 5 if aplicar_inflacao else ano_atual
            self.stdout.write(f'Ano final: {ano_fim_calc} (atual + 5 anos futuros)')
        
        self.stdout.write(f'Aplicar inflação futura (+5% ao ano): {"Sim" if aplicar_inflacao else "Não"}\n')
        
        try:
            resultado = service.atualizar_precos_automatico(
                uf=uf,
                ano_inicio=ano_inicio,
                ano_fim=ano_fim,
                aplicar_inflacao_futura=aplicar_inflacao
            )
            
            self.stdout.write(self.style.SUCCESS('\n>>> Atualizacao concluida com sucesso!\n'))
            self.stdout.write(f'Total de registros processados: {resultado["total_registros"]}')
            self.stdout.write(f'  - Novos registros criados: {resultado["criados"]}')
            self.stdout.write(f'  - Registros atualizados: {resultado["atualizados"]}')
            self.stdout.write(f'\nEstatisticas:')
            self.stdout.write(f'  - Estados processados: {resultado["estados"]}')
            self.stdout.write(f'  - Anos processados: {resultado["anos"]}')
            self.stdout.write(f'  - Categorias processadas: {resultado["categorias"]}')
            self.stdout.write(f'\n>>> Os precos foram atualizados com base em dados historicos reais do mercado.')
            if aplicar_inflacao:
                self.stdout.write(f'   Anos futuros foram calculados com +5% de inflacao anual.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n>>> ERRO ao atualizar precos: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def processar_anos(self, anos_str):
        """Processa string de anos (intervalo ou lista)"""
        anos = []
        
        if '-' in anos_str:
            # Intervalo: 2022-2026
            inicio, fim = map(int, anos_str.split('-'))
            anos = list(range(inicio, fim + 1))
        elif ',' in anos_str:
            # Lista: 2022,2023,2024
            anos = [int(a.strip()) for a in anos_str.split(',')]
        else:
            # Ano único
            anos = [int(anos_str)]
        
        return anos

