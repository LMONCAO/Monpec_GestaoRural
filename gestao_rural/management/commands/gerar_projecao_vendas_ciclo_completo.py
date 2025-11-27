# -*- coding: utf-8 -*-
"""
Comando para gerar projeções e vendas baseadas no ciclo completo de produção:
- Vacas de descarte: Canta Galo -> Invernada Grande (2022-2023) -> Vendas JBS
- Machos 12-24: Canta Galo -> Favo de Mel -> Girassol -> Vendas
- A partir de 2024: Vacas descarte -> Favo de Mel -> Girassol -> Vendas
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
# Usar timedelta ao invés de relativedelta para evitar dependência externa
# from dateutil.relativedelta import relativedelta

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada, InventarioRebanho, PlanejamentoAnual, CenarioPlanejamento
)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data, tratando corretamente mudanças de ano"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    # Ajustar ano e mês
    while mes > 12:
        mes -= 12
        ano += 1
    while mes < 1:
        mes += 12
        ano -= 1
    
    # Ajustar dia para meses com menos dias (ex: 31 de janeiro -> 28/29 de fevereiro)
    dias_no_mes = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    # Verificar ano bissexto
    if mes == 2 and (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)):
        dias_no_mes[2] = 29
    
    if dia > dias_no_mes[mes]:
        dia = dias_no_mes[mes]
    
    return date(ano, mes, dia)


class Command(BaseCommand):
    help = 'Gera projeções e vendas baseadas no ciclo completo de produção'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ano-inicio',
            type=int,
            default=2022,
            help='Ano inicial para gerar as projeções (padrão: 2022)'
        )
        parser.add_argument(
            '--ano-fim',
            type=int,
            default=2025,
            help='Ano final para gerar as projeções (padrão: 2025)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpar movimentações e vendas existentes antes de gerar'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        ano_inicio = options['ano_inicio']
        ano_fim = options['ano_fim']
        limpar = options['limpar']

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('GERAÇÃO DE PROJEÇÕES E VENDAS - CICLO COMPLETO'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # 1. Buscar propriedades
        propriedades = self._buscar_propriedades()
        if not propriedades:
            return

        canta_galo = propriedades['canta_galo']
        invernada_grande = propriedades['invernada_grande']
        favo_mel = propriedades['favo_mel']
        girassol = propriedades['girassol']

        # 2. Buscar categorias
        categorias = self._buscar_categorias()
        if not categorias:
            return

        # 3. Limpar dados existentes se solicitado
        if limpar:
            self._limpar_dados_existentes(canta_galo, ano_inicio, ano_fim)

        # 4. Buscar inventário inicial de Canta Galo (2022)
        inventario_inicial = self._buscar_inventario_inicial(canta_galo, ano_inicio)
        if not inventario_inicial:
            self.stdout.write(self.style.WARNING(
                f'[AVISO] Nenhum inventario encontrado para {canta_galo.nome_propriedade} em {ano_inicio}'
            ))
            self.stdout.write('   Criando inventário inicial estimado...')
            inventario_inicial = self._criar_inventario_estimado(canta_galo, ano_inicio, categorias)

        # 5. Processar ciclo 2022-2023
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('[CICLO 2022-2023] PROCESSANDO CICLO 2022-2023'))
        self.stdout.write('-' * 80)
        
        estoque_vacas_descarte = inventario_inicial.get('vacas_descarte', 0)
        estoque_machos_12_24 = inventario_inicial.get('machos_12_24', 0)
        
        # Transferir vacas de descarte para Invernada Grande
        if estoque_vacas_descarte > 0:
            data_transferencia = date(ano_inicio, 1, 15)
            self._criar_transferencia(
                origem=canta_galo,
                destino=invernada_grande,
                categoria=categorias['vaca_descarte'],
                quantidade=estoque_vacas_descarte,
                data=data_transferencia,
                observacao='Transferência inicial de vacas de descarte para engorda'
            )
            self.stdout.write(
                f'  [OK] Transferidas {estoque_vacas_descarte} vacas de descarte para {invernada_grande.nome_propriedade}'
            )
            
            # Vender 60 cabeças a cada 2 meses até zerar
            estoque_invernada = estoque_vacas_descarte
            data_venda = data_transferencia + timedelta(days=60)  # Primeira venda após 2 meses
            
            while estoque_invernada > 0 and data_venda.year <= 2023:
                quantidade_venda = min(60, estoque_invernada)
                self._criar_venda(
                    propriedade=invernada_grande,
                    categoria=categorias['vaca_gorda'],
                    quantidade=quantidade_venda,
                    data_venda=data_venda,
                    cliente_nome='JBS',
                    valor_por_kg=Decimal('6.50'),  # Preço estimado
                    peso_medio_kg=Decimal('450.00'),
                    observacao='Venda de vacas gordas para JBS'
                )
                estoque_invernada -= quantidade_venda
                self.stdout.write(
                    f'  [OK] Vendidas {quantidade_venda} vacas gordas para JBS em {data_venda.strftime("%d/%m/%Y")} '
                    f'(Estoque restante: {estoque_invernada})'
                )
                # Adicionar 2 meses
                data_venda = adicionar_meses(data_venda, 2)
        
        # Processar machos 12-24 meses
        if estoque_machos_12_24 > 0:
            data_transferencia = date(ano_inicio, 1, 20)
            self._criar_transferencia(
                origem=canta_galo,
                destino=favo_mel,
                categoria=categorias['macho_12_24'],
                quantidade=estoque_machos_12_24,
                data=data_transferencia,
                observacao='Transferência inicial de machos para recria'
            )
            self.stdout.write(
                f'  [OK] Transferidos {estoque_machos_12_24} machos 12-24 meses para {favo_mel.nome_propriedade}'
            )
            
            # Transferir 300 a cada 3 meses para Girassol
            estoque_favo_mel = estoque_machos_12_24
            data_transferencia_girassol = adicionar_meses(data_transferencia, 3)
            
            while estoque_favo_mel > 0 and data_transferencia_girassol.year <= 2023:
                quantidade_transferencia = min(300, estoque_favo_mel)
                
                # Transferir para Girassol
                self._criar_transferencia(
                    origem=favo_mel,
                    destino=girassol,
                    categoria=categorias['macho_12_24'],
                    quantidade=quantidade_transferencia,
                    data=data_transferencia_girassol,
                    observacao='Transferência para engorda em Girassol'
                )
                estoque_favo_mel -= quantidade_transferencia
                
                # Vender após 90 dias em Girassol
                data_venda_girassol = data_transferencia_girassol + timedelta(days=90)
                if data_venda_girassol.year <= 2023:
                    self._criar_venda(
                        propriedade=girassol,
                        categoria=categorias['boi_gordo'],
                        quantidade=quantidade_transferencia,
                        data_venda=data_venda_girassol,
                        cliente_nome='Frigorífico',
                        valor_por_kg=Decimal('7.00'),
                        peso_medio_kg=Decimal('500.00'),
                        observacao='Venda de gado gordo após 90 dias de engorda'
                    )
                    self.stdout.write(
                        f'  [OK] Transferidos {quantidade_transferencia} para {girassol.nome_propriedade} '
                        f'em {data_transferencia_girassol.strftime("%d/%m/%Y")}'
                    )
                    self.stdout.write(
                        f'  [OK] Vendidos {quantidade_transferencia} gordos em {data_venda_girassol.strftime("%d/%m/%Y")}'
                    )
                
                data_transferencia_girassol = adicionar_meses(data_transferencia_girassol, 3)

        # 6. Processar ciclo a partir de 2024
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('[CICLO 2024+] PROCESSANDO CICLO A PARTIR DE 2024'))
        self.stdout.write('-' * 80)
        
        # Buscar novas vacas de descarte geradas em 2024
        # Assumindo que há uma taxa de descarte anual (ex: 15% das matrizes)
        # Vou buscar o inventário de 2024 ou estimar
        
        # Para simplificar, vou processar de 2024 até ano_fim
        for ano in range(2024, ano_fim + 1):
            # Buscar ou estimar vacas de descarte do ano
            vacas_descarte_ano = self._estimar_vacas_descarte_ano(canta_galo, ano, categorias)
            
            if vacas_descarte_ano > 0:
                # Transferir para Favo de Mel em janeiro
                data_transferencia = date(ano, 1, 15)
                self._criar_transferencia(
                    origem=canta_galo,
                    destino=favo_mel,
                    categoria=categorias['vaca_descarte'],
                    quantidade=vacas_descarte_ano,
                    data=data_transferencia,
                    observacao=f'Transferência de vacas de descarte {ano} para recria'
                )
                self.stdout.write(
                    f'  [OK] {ano}: Transferidas {vacas_descarte_ano} vacas de descarte para {favo_mel.nome_propriedade}'
                )
                
                # Transferir para Girassol a cada 3 meses (100 cabeças por vez)
                estoque_favo_mel = vacas_descarte_ano
                data_transferencia_girassol = adicionar_meses(data_transferencia, 3)
                
                while estoque_favo_mel > 0 and data_transferencia_girassol.year <= ano_fim:
                    quantidade_transferencia = min(100, estoque_favo_mel)
                    
                    # Transferir para Girassol
                    self._criar_transferencia(
                        origem=favo_mel,
                        destino=girassol,
                        categoria=categorias['vaca_descarte'],
                        quantidade=quantidade_transferencia,
                        data=data_transferencia_girassol,
                        observacao='Transferência para engorda em Girassol'
                    )
                    estoque_favo_mel -= quantidade_transferencia
                    
                    # Vender após 90 dias em Girassol
                    data_venda_girassol = data_transferencia_girassol + timedelta(days=90)
                    if data_venda_girassol.year <= ano_fim:
                        self._criar_venda(
                            propriedade=girassol,
                            categoria=categorias['vaca_gorda'],
                            quantidade=quantidade_transferencia,
                            data_venda=data_venda_girassol,
                            cliente_nome='Frigorífico',
                            valor_por_kg=Decimal('6.50'),
                            peso_medio_kg=Decimal('450.00'),
                            observacao='Venda de vacas gordas após 90 dias de engorda'
                        )
                        self.stdout.write(
                            f'  [OK] Transferidos {quantidade_transferencia} para {girassol.nome_propriedade} '
                            f'em {data_transferencia_girassol.strftime("%d/%m/%Y")}'
                        )
                        self.stdout.write(
                            f'  [OK] Vendidos {quantidade_transferencia} gordos em {data_venda_girassol.strftime("%d/%m/%Y")}'
                        )
                    
                    # Adicionar 3 meses
                    if data_transferencia_girassol.month >= 10:
                        data_transferencia_girassol = date(data_transferencia_girassol.year + 1, data_transferencia_girassol.month - 9, data_transferencia_girassol.day)
                    else:
                        data_transferencia_girassol = date(data_transferencia_girassol.year, data_transferencia_girassol.month + 3, data_transferencia_girassol.day)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('[SUCESSO] PROJECOES E VENDAS GERADAS COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

    def _buscar_propriedades(self):
        """Busca as propriedades necessárias"""
        propriedades = {}
        
        nomes = {
            'canta_galo': ['Canta Galo', 'CANTA GALO', 'CantaGalo'],
            'invernada_grande': ['Invernada Grande', 'INVERNADA GRANDE', 'Invernada'],
            'favo_mel': ['Favo de Mel', 'FAVO DE MEL', 'Favo'],
            'girassol': ['Girassol', 'GIRASSOL']
        }
        
        for key, variacoes in nomes.items():
            propriedade = None
            for variacao in variacoes:
                propriedade = Propriedade.objects.filter(
                    nome_propriedade__icontains=variacao
                ).first()
                if propriedade:
                    break
            
            if not propriedade:
                self.stdout.write(self.style.ERROR(
                    f'[ERRO] Propriedade nao encontrada: {variacoes[0]}'
                ))
                return None
            
            propriedades[key] = propriedade
            self.stdout.write(
                f'[OK] {propriedade.nome_propriedade} encontrada (ID: {propriedade.id})'
            )
        
        return propriedades

    def _buscar_categorias(self):
        """Busca as categorias necessárias"""
        categorias = {}
        
        # Mapeamento de nomes de categorias
        mapeamento = {
            'vaca_descarte': ['Vaca Descarte', 'Vaca de Descarte', 'Descarte', 'Vacas Descarte', 'Vacas Descarte +36 M'],
            'vaca_gorda': ['Vaca Gorda', 'Vaca Engordada', 'Gorda', 'Vaca Gorda'],
            'macho_12_24': ['Macho 12-24', 'Macho 12 a 24', 'Macho', 'Novilho', 'Garrote 12-24 M', 'Garrote', 'Garrote 12-24'],
            'boi_gordo': ['Boi Gordo', 'Gordo', 'Boi Engordado', 'Boi 24-36 M', 'Boi'],
        }
        
        for key, nomes in mapeamento.items():
            categoria = None
            for nome in nomes:
                categoria = CategoriaAnimal.objects.filter(
                    nome__icontains=nome
                ).first()
                if categoria:
                    break
            
            if not categoria:
                self.stdout.write(self.style.WARNING(
                    f'[AVISO] Categoria nao encontrada: {nomes[0]}. Tentando criar...'
                ))
                # Tentar criar categoria básica
                categoria = CategoriaAnimal.objects.create(
                    nome=nomes[0],
                    descricao=f'Categoria {nomes[0]} criada automaticamente'
                )
                self.stdout.write(f'  [OK] Categoria criada: {categoria.nome}')
            
            categorias[key] = categoria
        
        return categorias

    def _buscar_inventario_inicial(self, propriedade, ano):
        """Busca o inventário inicial da propriedade"""
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario__year=ano
        ).order_by('-data_inventario').first()
        
        if not inventario:
            return None
        
        # Buscar todos os inventários do ano
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario__year=ano
        ).select_related('categoria')
        
        resultado = {}
        for inv in inventarios:
            nome_cat = inv.categoria.nome.lower()
            # Vacas de descarte
            if 'descarte' in nome_cat or ('vaca' in nome_cat and 'descarte' in nome_cat):
                resultado['vacas_descarte'] = resultado.get('vacas_descarte', 0) + inv.quantidade
            # Machos 12-24 meses (garrote, novilho, macho 12-24, etc)
            elif any(palavra in nome_cat for palavra in ['garrote', 'novilho', 'macho 12', 'macho 12-24', '12-24', '12 a 24']):
                resultado['machos_12_24'] = resultado.get('machos_12_24', 0) + inv.quantidade
        
        # Se não encontrou nada, retornar None para usar estimativa
        if not resultado:
            return None
        
        return resultado

    def _criar_inventario_estimado(self, propriedade, ano, categorias):
        """Cria um inventário estimado se não existir"""
        # Valores estimados baseados em uma fazenda típica
        return {
            'vacas_descarte': 200,  # Estimativa
            'machos_12_24': 500,    # Estimativa
        }

    def _estimar_vacas_descarte_ano(self, propriedade, ano, categorias):
        """Estima a quantidade de vacas de descarte para um ano"""
        # Buscar inventário de matrizes do ano anterior
        inventario_anterior = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario__year=ano - 1
        ).select_related('categoria')
        
        total_matrizes = 0
        for inv in inventario_anterior:
            nome_cat = inv.categoria.nome.lower()
            if 'matriz' in nome_cat or 'vaca' in nome_cat:
                total_matrizes += inv.quantidade
        
        # Taxa de descarte típica: 15-20%
        taxa_descarte = Decimal('0.15')
        return int(total_matrizes * taxa_descarte) if total_matrizes > 0 else 150

    def _criar_transferencia(self, origem, destino, categoria, quantidade, data, observacao=''):
        """Cria movimentações de transferência"""
        # Saída da origem
        MovimentacaoProjetada.objects.create(
            propriedade=origem,
            categoria=categoria,
            data_movimentacao=data,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade,
            observacao=f'Transferência para {destino.nome_propriedade}. {observacao}'
        )
        
        # Entrada no destino
        MovimentacaoProjetada.objects.create(
            propriedade=destino,
            categoria=categoria,
            data_movimentacao=data,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=quantidade,
            observacao=f'Transferência de {origem.nome_propriedade}. {observacao}'
        )

    def _criar_venda(self, propriedade, categoria, quantidade, data_venda, 
                     cliente_nome, valor_por_kg, peso_medio_kg, observacao=''):
        """Cria uma venda projetada"""
        peso_total = peso_medio_kg * Decimal(str(quantidade))
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(quantidade))
        
        # Criar movimentação de venda
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=propriedade,
            categoria=categoria,
            data_movimentacao=data_venda,
            tipo_movimentacao='VENDA',
            quantidade=quantidade,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            observacao=observacao
        )
        
        # Criar venda projetada
        VendaProjetada.objects.create(
            propriedade=propriedade,
            categoria=categoria,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda,
            quantidade=quantidade,
            cliente_nome=cliente_nome,
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_total,
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda + timedelta(days=30),
            observacoes=observacao
        )

    def _limpar_dados_existentes(self, propriedade, ano_inicio, ano_fim):
        """Limpa movimentações e vendas existentes"""
        self.stdout.write('[LIMPEZA] Limpando dados existentes...')
        
        # Limpar movimentações
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade__produtor=propriedade.produtor,
            data_movimentacao__year__gte=ano_inicio,
            data_movimentacao__year__lte=ano_fim
        )
        count_mov = movimentacoes.count()
        movimentacoes.delete()
        self.stdout.write(f'  [OK] {count_mov} movimentacoes removidas')
        
        # Limpar vendas
        vendas = VendaProjetada.objects.filter(
            propriedade__produtor=propriedade.produtor,
            data_venda__year__gte=ano_inicio,
            data_venda__year__lte=ano_fim
        )
        count_vendas = vendas.count()
        vendas.delete()
        self.stdout.write(f'  [OK] {count_vendas} vendas removidas')

