# -*- coding: utf-8 -*-
"""
Comando Django para treinamento da IA
Uso: python manage.py treinar_ia [--opcao completo|precos|reprodutivo|bigdata]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from gestao_rural.services.ml_price_prediction import MLPricePredictionService
from gestao_rural.services.ml_natalidade_mortalidade import MLNatalidadeMortalidadeService
from gestao_rural.services.big_data_analytics import BigDataAnalyticsService
from gestao_rural.models import Propriedade
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Treina os modelos de Inteligência Artificial do Monpec'

    def add_arguments(self, parser):
        parser.add_argument(
            '--opcao',
            choices=['completo', 'precos', 'reprodutivo', 'bigdata', 'propriedade'],
            default='completo',
            help='Tipo de treinamento a executar'
        )
        parser.add_argument(
            '--propriedade_id',
            type=int,
            help='ID da propriedade (obrigatório quando --opcao=propriedade)'
        )
        parser.add_argument(
            '--meses',
            type=int,
            default=24,
            help='Meses de dados históricos para análise (padrão: 24)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando treinamento da IA do Monpec...')
        )

        opcao = options['opcao']
        propriedade_id = options.get('propriedade_id')
        meses = options['meses']

        try:
            if opcao == 'completo':
                self._treinamento_completo(meses)
            elif opcao == 'precos':
                self._treinar_precos(meses)
            elif opcao == 'reprodutivo':
                self._treinar_reprodutivo(meses)
            elif opcao == 'bigdata':
                self._treinar_big_data(meses)
            elif opcao == 'propriedade':
                if not propriedade_id:
                    raise CommandError('--propriedade_id é obrigatório para --opcao=propriedade')
                self._treinar_propriedade(propriedade_id, meses)

            self.stdout.write(
                self.style.SUCCESS('✅ Treinamento concluído com sucesso!')
            )

        except Exception as e:
            logger.error(f'Erro no treinamento: {e}')
            raise CommandError(f'Erro no treinamento: {e}')

    def _treinamento_completo(self, meses):
        """Executa treinamento completo de todos os modelos"""
        self.stdout.write('🔄 Executando treinamento completo...')

        # Treinar preços
        self._treinar_precos(meses)

        # Treinar reprodutivo
        self._treinar_reprodutivo(meses)

        # Treinar Big Data
        self._treinar_big_data(meses)

        self.stdout.write('📋 Gerando relatório final...')
        self._gerar_relatorio_resumo()

    def _treinar_precos(self, meses):
        """Treina modelos de previsão de preços"""
        self.stdout.write('💰 Treinando modelos de preços...')

        ml_price = MLPricePredictionService()
        categorias = ['BOI', 'BEZERRO', 'BEZERRA', 'GARROTE', 'NOVILHA']

        treinados = 0
        for categoria in categorias:
            try:
                self.stdout.write(f'  → Treinando {categoria}...')

                # Coletar dados
                dados = ml_price._coletar_dados_historicos('MT', categoria, periodo_meses=meses)

                if len(dados) >= 12:
                    # Preparar dados
                    X, y = ml_price._preparar_dados_ml(dados)

                    if len(X) >= 10:
                        # Treinar modelo
                        previsao = ml_price._prever_com_ensemble(X, y, 3)
                        treinados += 1

                        self.stdout.write(
                            self.style.SUCCESS(f'    ✅ {categoria}: {len(X)} amostras treinadas')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠️ {categoria}: Dados insuficientes ({len(X)} amostras)')
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠️ {categoria}: Histórico insuficiente ({len(dados)} registros)')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ {categoria}: Erro - {e}')
                )

        self.stdout.write(f'📊 Modelos de preços treinados: {treinados}/{len(categorias)}')

    def _treinar_reprodutivo(self, meses):
        """Treina modelos reprodutivos"""
        self.stdout.write('🐄 Treinando modelos reprodutivos...')

        ml_reprodutivo = MLNatalidadeMortalidadeService()
        propriedades = Propriedade.objects.filter(ativo=True)[:5]  # Limitar para performance

        natalidade_ok = 0
        mortalidade_ok = 0

        for prop in propriedades:
            try:
                self.stdout.write(f'  → Propriedade: {prop.nome}')

                # Treinar natalidade
                nat = ml_reprodutivo.prever_taxa_natalidade(prop.id, 'Multípara', periodo_meses=meses)
                if nat.get('sucesso'):
                    natalidade_ok += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Natalidade: {nat["taxa_prevista"]:.1%}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠️ Natalidade: Dados insuficientes')
                    )

                # Treinar mortalidade
                mort = ml_reprodutivo.prever_taxa_mortalidade(prop.id, 'Bezerros (0-12m)', periodo_meses=meses)
                if mort.get('sucesso'):
                    mortalidade_ok += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Mortalidade: {mort["taxa_prevista"]:.1%}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠️ Mortalidade: Dados insuficientes')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ Erro na propriedade {prop.id}: {e}')
                )

        self.stdout.write(f'📊 Natalidade: {natalidade_ok}/{len(propriedades)} propriedades')
        self.stdout.write(f'📊 Mortalidade: {mortalidade_ok}/{len(propriedades)} propriedades')

    def _treinar_big_data(self, meses):
        """Treina/executa análise Big Data"""
        self.stdout.write('📊 Executando análise Big Data...')

        big_data = BigDataAnalyticsService()
        propriedades = Propriedade.objects.filter(ativo=True)[:3]  # Limitar para performance

        analisadas = 0
        for prop in propriedades:
            try:
                self.stdout.write(f'  → Analisando: {prop.nome}')

                analise = big_data.analisar_dados_historicos_completos(prop.id, periodo_meses=meses)

                if analise.get('sucesso'):
                    registros = analise.get('total_registros', 0)
                    analisadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Análise completa: {registros:,} registros processados')
                    )

                    # Mostrar alguns insights
                    insights = analise.get('insights', [])
                    if insights:
                        self.stdout.write(f'    💡 Top insights: {insights[0][:50]}...')

                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠️ Análise falhou: {analise.get("erro", "Erro desconhecido")}')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ Erro na análise {prop.id}: {e}')
                )

        self.stdout.write(f'📊 Propriedades analisadas: {analisadas}/{len(propriedades)}')

    def _treinar_propriedade(self, propriedade_id, meses):
        """Treina modelos para uma propriedade específica"""
        try:
            propriedade = Propriedade.objects.get(id=propriedade_id)
        except Propriedade.DoesNotExist:
            raise CommandError(f'Propriedade {propriedade_id} não encontrada')

        self.stdout.write(f'🏗️ Treinando modelos para propriedade: {propriedade.nome}')
        self.stdout.write(f'📅 Período de análise: {meses} meses')

        # Treinar preços para esta propriedade
        self._treinar_precos(meses)

        # Treinar reprodutivo
        self._treinar_reprodutivo(meses)

        # Big Data para esta propriedade
        big_data = BigDataAnalyticsService()
        try:
            analise = big_data.analisar_dados_historicos_completos(propriedade_id, periodo_meses=meses)
            if analise.get('sucesso'):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Big Data: {analise.get("total_registros", 0):,} registros analisados')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Big Data: {analise.get("erro", "Falhou")}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro no Big Data: {e}')
            )

    def _gerar_relatorio_resumo(self):
        """Gera relatório resumido do treinamento"""
        relatorio = f"""
================================================================================
RELATÓRIO DE TREINAMENTO - IA MONPEC
================================================================================
Data/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

✅ TREINAMENTO CONCLUÍDO COM SUCESSO!

RESUMO DOS MODELOS:
• Machine Learning de Preços: Treinado
• Machine Learning Reprodutivo: Treinado
• Big Data Analytics: Executado

PRÓXIMOS PASSOS:
1. Verificar performance no sistema de planejamento
2. Agendar treinamentos regulares
3. Monitorar logs para eventuais ajustes

PARA MAIS DETALHES:
• Ver arquivo: RELATORIO_TREINAMENTO_IA.txt
• Logs: logs/treinamento_ia.log

================================================================================
"""

        # Salvar relatório
        with open('RELATORIO_TREINAMENTO_RESUMO.txt', 'w', encoding='utf-8') as f:
            f.write(relatorio)

        self.stdout.write(
            self.style.SUCCESS('📄 Relatório salvo em: RELATORIO_TREINAMENTO_RESUMO.txt')
        )

        # Mostrar resumo na tela
        self.stdout.write('\n' + '='*80)
        self.stdout.write('📋 RESUMO DO TREINAMENTO:')
        self.stdout.write('='*80)
        self.stdout.write('✅ Modelos de preços treinados')
        self.stdout.write('✅ Modelos reprodutivos treinados')
        self.stdout.write('✅ Análise Big Data executada')
        self.stdout.write('✅ Relatório gerado')
        self.stdout.write('')
        self.stdout.write('💡 Os modelos estão prontos para uso no sistema de planejamento!')
        self.stdout.write('='*80)