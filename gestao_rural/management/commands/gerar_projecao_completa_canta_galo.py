# -*- coding: utf-8 -*-
"""
Comando para gerar projeções completas baseadas nas regras específicas:
- Fazenda Canta Galo: Nascimentos 80%, Mortes 9%/2%, Vendas 30%/20%, Transferências
- Fazenda Invernada Grande (2022-2023): Recebe descarte, vende lotes de 60
- Fazenda Favo de Mel (2024+): Recebe descarte e machos, transfere 480 cabeças para Girassol a cada 90 dias
- Fazenda Girassol: Recebe machos, engorda, vende a cada 90 dias

================================================================================
REGRAS PERMANENTES - CONFIGURAÇÃO PADRÃO CANTA GALO:
================================================================================

1. TRANSFERÊNCIAS DE VACAS DESCARTE:
   - REGRA CRÍTICA: NÃO TRANSFERIR SE SALDO FOR NEGATIVO OU ZERO
   - Sempre verificar saldo REAL após promoções antes de criar transferência
   - Transferir apenas se houver saldo disponível suficiente
   - Anos permitidos: 2022-2023 (Invernada Grande), 2024+ (Favo de Mel)

2. TAXA DE NATALIDADE:
   - Padrão: 80% das matrizes (alterado de 70% para 80%)

3. VENDAS:
   - Bezerras Fêmeas: 30% (alterado de 20% para 30%)
   - Bezerros Machos: 20% (mantido)

4. EVOLUÇÕES:
   - Todas as promoções devem ser criadas ANTES das transferências
   - Saldo após promoções deve ser verificado antes de transferir

================================================================================
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from collections import defaultdict

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada, InventarioRebanho, ParametrosProjecaoRebanho
)
from django.db.models import Sum


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
    
    # Ajustar dia para meses com menos dias
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


def calcular_rebanho_por_movimentacoes(propriedade, data_referencia):
    """
    Calcula o rebanho atual baseado no inventário inicial + movimentações projetadas.
    Similar à lógica usada nas projeções da Fazenda Canta Galo.
    """
    from collections import defaultdict
    
    # Buscar inventário inicial (mais recente antes da data de referência)
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    if not inventario_inicial:
        return {}
    
    # Buscar todos os inventários da mesma data
    data_inventario = inventario_inicial.data_inventario
    inventarios = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario=data_inventario
    ).select_related('categoria')
    
    # Inicializar saldos com inventário inicial
    saldos = defaultdict(int)
    for inv in inventarios:
        saldos[inv.categoria.nome] = inv.quantidade
    
    # Aplicar todas as movimentações até a data de referência
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__gt=data_inventario,
        data_movimentacao__lte=data_referencia
    ).select_related('categoria')
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldos[categoria] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldos[categoria] -= mov.quantidade
            # Garantir que não fique negativo
            if saldos[categoria] < 0:
                saldos[categoria] = 0
    
    return dict(saldos)
    
    return date(ano, mes, dia)


class Command(BaseCommand):
    help = 'Gera projeções completas baseadas nas regras específicas da Fazenda Canta Galo'

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
        self.stdout.write(self.style.SUCCESS('GERAÇÃO DE PROJEÇÕES COMPLETAS - FAZENDA CANTA GALO'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # 1. Buscar propriedades
        propriedades = self._buscar_propriedades()
        if not propriedades:
            return

        canta_galo = propriedades['canta_galo']
        invernada_grande = propriedades.get('invernada_grande')
        favo_mel = propriedades.get('favo_mel')
        girassol = propriedades.get('girassol')

        # 2. Buscar categorias
        categorias = self._buscar_categorias()
        if not categorias:
            self.stdout.write(self.style.ERROR('[ERRO] Nenhuma categoria encontrada!'))
            return
        
        self.stdout.write('')
        self.stdout.write('[CATEGORIAS] Categorias encontradas:')
        for key, cat in categorias.items():
            self.stdout.write(f'  - {key}: {cat.nome} (ID: {cat.id})')

        # 3. Limpar dados existentes se solicitado
        if limpar:
            self._limpar_dados_existentes(canta_galo, ano_inicio, ano_fim)

        # 4. Buscar inventário inicial de Canta Galo
        inventario_inicial = self._buscar_inventario_inicial(canta_galo, ano_inicio)
        if not inventario_inicial:
            self.stdout.write(self.style.ERROR(
                f'[ERRO] Nenhum inventario encontrado para {canta_galo.nome_propriedade} em {ano_inicio}'
            ))
            return
        
        self.stdout.write('')
        self.stdout.write('[INVENTARIO INICIAL] Saldos iniciais:')
        for cat_nome, quantidade in inventario_inicial.items():
            self.stdout.write(f'  - {cat_nome}: {quantidade}')

        # 5. Processar cada ano
        saldos = inventario_inicial.copy()
        nascimentos_ano = defaultdict(int)  # Rastrear nascimentos do ano para vendas
        ano_inicio_var = ano_inicio  # Variável para usar na função de evolução
        
        for ano in range(ano_inicio, ano_fim + 1):
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'[ANO {ano}] PROCESSANDO ANO {ano}'))
            self.stdout.write('-' * 80)
            
            # Resetar nascimentos do ano
            nascimentos_ano.clear()
            
            # Processar mês a mês
            for mes in range(1, 13):
                data_mes = date(ano, mes, 15)
                
                # 1. NASCIMENTOS (80% das matrizes) - apenas julho a dezembro
                if mes >= 7:
                    nascimentos = self._processar_nascimentos(
                        canta_galo, data_mes, saldos, categorias, ano
                    )
                    for nasc in nascimentos:
                        saldos[nasc['categoria']] = saldos.get(nasc['categoria'], 0) + nasc['quantidade']
                        nascimentos_ano[nasc['categoria']] = nascimentos_ano.get(nasc['categoria'], 0) + nasc['quantidade']
                        self.stdout.write(f'  [MES {mes:02d}] Nascimentos: {nasc["quantidade"]} {nasc["categoria"]}')
                
                # 2. MORTES (9% dos nascimentos, 2% dos adultos acima de 12 meses)
                mortes = self._processar_mortes(
                    canta_galo, data_mes, saldos, categorias, ano
                )
                for morte in mortes:
                    saldos[morte['categoria']] = max(0, saldos.get(morte['categoria'], 0) - morte['quantidade'])
                    if morte['quantidade'] > 0:
                        self.stdout.write(f'  [MES {mes:02d}] Mortes: {morte["quantidade"]} {morte["categoria"]}')
                
                # 3. EVOLUÇÃO DE IDADE (antes das vendas) - APENAS animais que completaram 12 meses
                # Só evoluir animais nascidos há 12 meses ou mais
                evolucoes = self._processar_evolucao_idade(
                    canta_galo, data_mes, saldos, categorias, ano, nascimentos_ano, ano_inicio_var
                )
                for evol in evolucoes:
                    saldos[evol['categoria_origem']] = max(0, saldos.get(evol['categoria_origem'], 0) - evol['quantidade'])
                    saldos[evol['categoria_destino']] = saldos.get(evol['categoria_destino'], 0) + evol['quantidade']
                    if evol['quantidade'] > 0:
                        self.stdout.write(f'  [MES {mes:02d}] Evolucao: {evol["quantidade"]} {evol["categoria_origem"]} -> {evol["categoria_destino"]}')
                
                # 4. VENDAS (20% dos nascimentos do ANO, 20% das nulíparas)
                vendas = self._processar_vendas(
                    canta_galo, data_mes, saldos, categorias, ano, nascimentos_ano
                )
                for venda in vendas:
                    saldos[venda['categoria']] = max(0, saldos.get(venda['categoria'], 0) - venda['quantidade'])
                    if venda['quantidade'] > 0:
                        self.stdout.write(f'  [MES {mes:02d}] Vendas: {venda["quantidade"]} {venda["categoria"]}')
                
                # 5. TRANSFERÊNCIAS (janeiro de cada ano) - APENAS o que foi gerado no ano anterior
                if mes == 1:
                    transferencias = self._processar_transferencias(
                        canta_galo, data_mes, saldos, categorias, ano,
                        invernada_grande, favo_mel, girassol
                    )
                    for transf in transferencias:
                        saldos[transf['categoria']] = max(0, saldos.get(transf['categoria'], 0) - transf['quantidade'])
                        if transf['quantidade'] > 0:
                            self.stdout.write(f'  [MES {mes:02d}] Transferencias: {transf["quantidade"]} {transf["categoria"]}')
                
                # 6. Processar transferências e vendas nas outras fazendas
                # IMPORTANTE: Calcular saldos das outras fazendas antes de processar
                if invernada_grande and ano <= 2023:
                    # Calcular saldos da Invernada Grande
                    saldos_invernada = calcular_rebanho_por_movimentacoes(invernada_grande, data_mes)
                    self._processar_invernada_grande(
                        invernada_grande, data_mes, categorias, ano, saldos_invernada
                    )
                
                if favo_mel and ano >= 2024:
                    # Calcular saldos do Favo de Mel
                    saldos_favo_mel = calcular_rebanho_por_movimentacoes(favo_mel, data_mes)
                    self._processar_favo_mel(
                        favo_mel, data_mes, categorias, ano, saldos_favo_mel
                    )
                
                if girassol:
                    # Calcular saldos do Girassol
                    saldos_girassol = calcular_rebanho_por_movimentacoes(girassol, data_mes)
                    self._processar_girassol(
                        girassol, data_mes, categorias, ano, saldos_girassol
                    )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('[SUCESSO] PROJECOES GERADAS COM SUCESSO!'))
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
            
            if not propriedade and key == 'canta_galo':
                self.stdout.write(self.style.ERROR(
                    f'[ERRO] Propriedade nao encontrada: {variacoes[0]}'
                ))
                return None
            
            if propriedade:
                propriedades[key] = propriedade
                self.stdout.write(
                    f'[OK] {propriedade.nome_propriedade} encontrada (ID: {propriedade.id})'
                )
        
        return propriedades

    def _buscar_categorias(self):
        """Busca as categorias necessárias"""
        categorias = {}
        
        mapeamento = {
            'vaca_reproducao': ['Vaca em Reprodução', 'Vacas em Reprodução', 'Vaca Reprodução', 'Vacas Reprodução +36 M'],
            'vaca_descarte': ['Vaca Descarte', 'Vaca de Descarte', 'Descarte', 'Vacas Descarte'],
            'vaca_gorda': ['Vaca Gorda', 'Vaca Engordada', 'Gorda'],
            'nulipara': ['Nulípara', 'Nulipara', 'Novilha', 'Novilha 24-36 M'],
            'macho_12_24': ['Macho 12-24', 'Macho 12 a 24', 'Garrote 12-24 M', 'Garrote'],
            'boi_gordo_24_36': ['Boi Gordo 24-36', 'Boi 24-36 M', 'Boi Gordo', 'Boi Engordado'],
            'bezerro': ['Bezerro', 'Bezerro(o) 0-12 M', 'Bezerros (0-12m)'],
            'bezerra': ['Bezerra', 'Bezerro(a) 0-12 F', 'Bezerras (0-12m)'],
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
                    f'[AVISO] Categoria nao encontrada: {nomes[0]}'
                ))
                continue
            
            categorias[key] = categoria
        
        return categorias

    def _buscar_inventario_inicial(self, propriedade, ano):
        """Busca o inventário inicial da propriedade"""
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario__year=ano
        ).order_by('-data_inventario').select_related('categoria')
        
        if not inventarios.exists():
            # Buscar o mais recente disponível
            inventarios = InventarioRebanho.objects.filter(
                propriedade=propriedade
            ).order_by('-data_inventario').select_related('categoria')
        
        if not inventarios.exists():
            return None
        
        # Agrupar por categoria
        saldos = {}
        for inv in inventarios:
            cat_nome = inv.categoria.nome
            saldos[cat_nome] = saldos.get(cat_nome, 0) + inv.quantidade
        
        return saldos

    def _processar_nascimentos(self, propriedade, data, saldos, categorias, ano):
        """Processa nascimentos: 80% das matrizes (apenas julho a dezembro)"""
        nascimentos = []
        
        # Buscar matrizes (Vacas em Reprodução)
        matrizes = 0
        cat_vaca_reproducao = categorias.get('vaca_reproducao')
        
        if cat_vaca_reproducao:
            matrizes = saldos.get(cat_vaca_reproducao.nome, 0)
        
        if matrizes == 0:
            return nascimentos
        
        # Calcular nascimentos: 80% das matrizes, distribuído em 6 meses (julho a dezembro)
        taxa_natalidade = Decimal('0.80')
        total_nascimentos_ano = int(matrizes * taxa_natalidade)
        nascimentos_por_mes = total_nascimentos_ano // 6
        
        # No primeiro mês (julho), adicionar o resto
        mes_estacao = data.month - 6  # 0 a 5 (julho a dezembro)
        if mes_estacao == 0:
            nascimentos_mes = nascimentos_por_mes + (total_nascimentos_ano % 6)
        else:
            nascimentos_mes = nascimentos_por_mes
        
        if nascimentos_mes > 0:
            # Distribuir 50/50 entre bezerros e bezerras
            bezerros = nascimentos_mes // 2
            bezerras = nascimentos_mes - bezerros
            
            cat_bezerro = categorias.get('bezerro')
            cat_bezerra = categorias.get('bezerra')
            
            if cat_bezerro and bezerros > 0:
                MovimentacaoProjetada.objects.create(
                    propriedade=propriedade,
                    categoria=cat_bezerro,
                    data_movimentacao=data,
                    tipo_movimentacao='NASCIMENTO',
                    quantidade=bezerros,
                    observacao=f'Nascimentos automáticos - {bezerros} bezerros (80% das matrizes)'
                )
                nascimentos.append({'categoria': cat_bezerro.nome, 'quantidade': bezerros})
            
            if cat_bezerra and bezerras > 0:
                MovimentacaoProjetada.objects.create(
                    propriedade=propriedade,
                    categoria=cat_bezerra,
                    data_movimentacao=data,
                    tipo_movimentacao='NASCIMENTO',
                    quantidade=bezerras,
                    observacao=f'Nascimentos automáticos - {bezerras} bezerras (80% das matrizes)'
                )
                nascimentos.append({'categoria': cat_bezerra.nome, 'quantidade': bezerras})
        
        return nascimentos

    def _processar_mortes(self, propriedade, data, saldos, categorias, ano):
        """Processa mortes: 9% dos nascimentos, 2% dos adultos acima de 12 meses (TAXAS ANUAIS, distribuídas mensalmente) - SEMPRE verifica estoque"""
        mortes = []
        
        # IMPORTANTE: As taxas são ANUAIS, então dividimos por 12 para aplicar mensalmente
        # 1. Mortes de nascimentos (9% ANUAL = 0.75% mensal)
        bezerros = saldos.get(categorias.get('bezerro').nome, 0) if categorias.get('bezerro') else 0
        bezerras = saldos.get(categorias.get('bezerra').nome, 0) if categorias.get('bezerra') else 0
        total_nascimentos = bezerros + bezerras
        
        if total_nascimentos > 0:
            # Taxa anual de 9% = 0.75% mensal (9% / 12)
            taxa_morte_nascimentos_mensal = Decimal('0.09') / Decimal('12')
            mortes_nascimentos_calc = int(total_nascimentos * taxa_morte_nascimentos_mensal)
            
            if mortes_nascimentos_calc > 0:
                # Distribuir proporcionalmente
                if total_nascimentos > 0:
                    mortes_bezerros_calc = int(mortes_nascimentos_calc * (bezerros / total_nascimentos))
                    mortes_bezerras_calc = mortes_nascimentos_calc - mortes_bezerros_calc
                else:
                    mortes_bezerros_calc = 0
                    mortes_bezerras_calc = 0
                
                cat_bezerro = categorias.get('bezerro')
                cat_bezerra = categorias.get('bezerra')
                
                if cat_bezerro and mortes_bezerros_calc > 0:
                    # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                    mortes_bezerros = min(mortes_bezerros_calc, bezerros)
                    if mortes_bezerros > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_bezerro,
                            data_movimentacao=data,
                            tipo_movimentacao='MORTE',
                            quantidade=mortes_bezerros,
                            observacao=f'Mortes automáticas - {mortes_bezerros} bezerros (9% anual = 0.75% mensal) - Estoque disponível: {bezerros}'
                        )
                        mortes.append({'categoria': cat_bezerro.nome, 'quantidade': mortes_bezerros})
                
                if cat_bezerra and mortes_bezerras_calc > 0:
                    # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                    mortes_bezerras = min(mortes_bezerras_calc, bezerras)
                    if mortes_bezerras > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_bezerra,
                            data_movimentacao=data,
                            tipo_movimentacao='MORTE',
                            quantidade=mortes_bezerras,
                            observacao=f'Mortes automáticas - {mortes_bezerras} bezerras (9% anual = 0.75% mensal) - Estoque disponível: {bezerras}'
                        )
                        mortes.append({'categoria': cat_bezerra.nome, 'quantidade': mortes_bezerras})
        
        # 2. Mortes de adultos acima de 12 meses (2% ANUAL = 0.167% mensal)
        # Taxa anual de 2% = 0.167% mensal (2% / 12)
        taxa_morte_adultos_mensal = Decimal('0.02') / Decimal('12')
        categorias_adultos = [
            categorias.get('vaca_reproducao'),
            categorias.get('nulipara'),
            categorias.get('macho_12_24'),
        ]
        
        for cat in categorias_adultos:
            if cat:
                estoque = saldos.get(cat.nome, 0)
                if estoque > 0:
                    mortes_adultos_calc = int(estoque * taxa_morte_adultos_mensal)
                    # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                    mortes_adultos = min(mortes_adultos_calc, estoque)
                    if mortes_adultos > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat,
                            data_movimentacao=data,
                            tipo_movimentacao='MORTE',
                            quantidade=mortes_adultos,
                            observacao=f'Mortes automáticas - {mortes_adultos} adultos (2% anual = 0.167% mensal) - Estoque disponível: {estoque}'
                        )
                        mortes.append({'categoria': cat.nome, 'quantidade': mortes_adultos})
        
        return mortes

    def _processar_evolucao_idade(self, propriedade, data, saldos, categorias, ano, nascimentos_ano, ano_inicio):
        """Processa evolução de idade (antes das vendas) - APENAS animais que completaram 12 meses"""
        evolucoes = []
        
        # IMPORTANTE: Evoluir apenas animais que completaram 12 meses
        # Simplificação: evoluir mensalmente 1/12 dos animais que estão na categoria há 12 meses
        # Mas para evitar complexidade, vamos evoluir apenas em janeiro (animais nascidos no ano anterior)
        
        cat_bezerro = categorias.get('bezerro')
        cat_bezerra = categorias.get('bezerra')
        cat_nulipara = categorias.get('nulipara')
        cat_macho_12_24 = categorias.get('macho_12_24')
        cat_boi_gordo = categorias.get('boi_gordo_24_36')
        cat_vaca_reproducao = categorias.get('vaca_reproducao')
        
        # Evoluir apenas em janeiro (animais nascidos no ano anterior que completaram 12 meses)
        if data.month == 1 and ano > ano_inicio:
            # Buscar nascimentos do ano anterior
            nascimentos_ano_anterior = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='NASCIMENTO',
                data_movimentacao__year=ano - 1
            ).select_related('categoria')
            
            # Agrupar por categoria
            nascimentos_por_cat = defaultdict(int)
            for nasc in nascimentos_ano_anterior:
                nascimentos_por_cat[nasc.categoria.nome] += nasc.quantidade
            
            # Bezerros → Machos 12-24 (evoluir apenas os bezerros MACHOS que nasceram no ano anterior)
            # Como temos bezerros e bezerras separados, vamos evoluir os bezerros (machos)
            if cat_bezerro and cat_macho_12_24:
                bezerros_nascidos = nascimentos_por_cat.get(cat_bezerro.nome, 0)
                if bezerros_nascidos > 0:
                    # Verificar estoque disponível
                    estoque_bezerros = saldos.get(cat_bezerro.nome, 0)
                    evolucao = min(bezerros_nascidos, estoque_bezerros)
                    
                    if evolucao > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_bezerro,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Bezerros → Machos 12-24 (nascidos em {ano-1})'
                        )
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_macho_12_24,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Bezerros → Machos 12-24 (nascidos em {ano-1})'
                        )
                        evolucoes.append({
                            'categoria_origem': cat_bezerro.nome,
                            'categoria_destino': cat_macho_12_24.nome,
                            'quantidade': evolucao
                        })
            
            # Bezerras → Nulíparas
            if cat_bezerra and cat_nulipara:
                bezerras_nascidas = nascimentos_por_cat.get(cat_bezerra.nome, 0)
                if bezerras_nascidas > 0:
                    # Verificar estoque disponível
                    estoque_bezerras = saldos.get(cat_bezerra.nome, 0)
                    evolucao = min(bezerras_nascidas, estoque_bezerras)
                    
                    if evolucao > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_bezerra,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Bezerras → Nulíparas (nascidas em {ano-1})'
                        )
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_nulipara,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Bezerras → Nulíparas (nascidas em {ano-1})'
                        )
                        evolucoes.append({
                            'categoria_origem': cat_bezerra.nome,
                            'categoria_destino': cat_nulipara.nome,
                            'quantidade': evolucao
                        })
            
            # Nulíparas → Vacas em Reprodução (evoluir nulíparas do ano anterior)
            if cat_nulipara and cat_vaca_reproducao:
                # Buscar nulíparas que evoluíram no ano anterior
                nuliparas_ano_anterior = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='PROMOCAO_ENTRADA',
                    categoria=cat_nulipara,
                    data_movimentacao__year=ano - 1
                ).aggregate(total=Sum('quantidade'))['total'] or 0
                
                if nuliparas_ano_anterior > 0:
                    # Evoluir 80% das nulíparas (as que ficaram prenhas)
                    evolucao_total = int(nuliparas_ano_anterior * Decimal('0.80'))
                    # Verificar estoque disponível
                    estoque_nuliparas = saldos.get(cat_nulipara.nome, 0)
                    evolucao = min(evolucao_total, estoque_nuliparas)
                    
                    if evolucao > 0:
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_nulipara,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Nulíparas → Vacas em Reprodução (80% prenhas)'
                        )
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            categoria=cat_vaca_reproducao,
                            data_movimentacao=data,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            quantidade=evolucao,
                            observacao=f'Evolução de idade: Nulíparas → Vacas em Reprodução (80% prenhas)'
                        )
                        evolucoes.append({
                            'categoria_origem': cat_nulipara.nome,
                            'categoria_destino': cat_vaca_reproducao.nome,
                            'quantidade': evolucao
                        })
        
        return evolucoes

    def _processar_vendas(self, propriedade, data, saldos, categorias, ano, nascimentos_ano):
        """Processa vendas: 20% dos nascimentos do ANO, 20% das nulíparas - SEMPRE verifica estoque"""
        vendas = []
        
        # 1. Vendas de 20% dos nascimentos do ANO (distribuído ao longo do ano após nascimentos)
        # Só vender após julho (quando começam os nascimentos)
        # IMPORTANTE: Vender 20% do TOTAL de nascimentos do ano, não acumulado
        if data.month >= 7:
            cat_bezerro = categorias.get('bezerro')
            cat_bezerra = categorias.get('bezerra')
            
            # Calcular total de nascimentos do ano até agora
            total_nascimentos_ano = sum(nascimentos_ano.values())
            
            if total_nascimentos_ano > 0:
                # Vender 20% dos nascimentos do ano, distribuído nos meses após julho (julho a dezembro = 6 meses)
                # Mas só vender após os nascimentos começarem
                meses_venda = max(1, 13 - data.month)  # Meses de venda restantes (julho a dezembro)
                vendas_totais_ano = int(total_nascimentos_ano * Decimal('0.20'))
                
                # Distribuir igualmente pelos meses restantes
                vendas_mes = vendas_totais_ano // meses_venda if meses_venda > 0 else 0
                
                if cat_bezerro and nascimentos_ano.get(cat_bezerro.nome, 0) > 0:
                    bezerros_nascidos = nascimentos_ano.get(cat_bezerro.nome, 0)
                    proporcao_bezerros = Decimal(str(bezerros_nascidos)) / Decimal(str(total_nascimentos_ano)) if total_nascimentos_ano > 0 else Decimal('0.50')
                    vendas_bezerros_calc = int(vendas_mes * proporcao_bezerros)
                    
                    if vendas_bezerros_calc > 0:
                        # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                        estoque_bezerros = saldos.get(cat_bezerro.nome, 0)
                        vendas_bezerros = min(vendas_bezerros_calc, estoque_bezerros)
                        
                        if vendas_bezerros > 0:
                            self._criar_venda(
                                propriedade=propriedade,
                                categoria=cat_bezerro,
                                quantidade=vendas_bezerros,
                                data_venda=data,
                                cliente_nome='Cliente',
                                valor_por_kg=Decimal('8.00'),
                                peso_medio_kg=Decimal('200.00'),
                                observacao=f'Venda de 20% dos nascimentos do ano (bezerros) - Estoque disponível: {estoque_bezerros}'
                            )
                            vendas.append({'categoria': cat_bezerro.nome, 'quantidade': vendas_bezerros})
                
                if cat_bezerra and nascimentos_ano.get(cat_bezerra.nome, 0) > 0:
                    bezerras_nascidas = nascimentos_ano.get(cat_bezerra.nome, 0)
                    proporcao_bezerras = Decimal(str(bezerras_nascidas)) / Decimal(str(total_nascimentos_ano)) if total_nascimentos_ano > 0 else Decimal('0.50')
                    vendas_bezerras_calc = int(vendas_mes * proporcao_bezerras)
                    
                    if vendas_bezerras_calc > 0:
                        # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                        estoque_bezerras = saldos.get(cat_bezerra.nome, 0)
                        vendas_bezerras = min(vendas_bezerras_calc, estoque_bezerras)
                        
                        if vendas_bezerras > 0:
                            self._criar_venda(
                                propriedade=propriedade,
                                categoria=cat_bezerra,
                                quantidade=vendas_bezerras,
                                data_venda=data,
                                cliente_nome='Cliente',
                                valor_por_kg=Decimal('8.00'),
                                peso_medio_kg=Decimal('200.00'),
                                observacao=f'Venda de 20% dos nascimentos do ano (bezerras) - Estoque disponível: {estoque_bezerras}'
                            )
                            vendas.append({'categoria': cat_bezerra.nome, 'quantidade': vendas_bezerras})
        
        # 2. Vendas de 20% das nulíparas (descarte) - apenas em julho
        cat_nulipara = categorias.get('nulipara')
        if cat_nulipara and data.month == 7:
            estoque_nuliparas = saldos.get(cat_nulipara.nome, 0)
            if estoque_nuliparas > 0:
                vendas_nuliparas_calc = int(estoque_nuliparas * Decimal('0.20'))
                # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
                vendas_nuliparas = min(vendas_nuliparas_calc, estoque_nuliparas)
                
                if vendas_nuliparas > 0:
                    self._criar_venda(
                        propriedade=propriedade,
                        categoria=cat_nulipara,
                        quantidade=vendas_nuliparas,
                        data_venda=data,
                        cliente_nome='Cliente',
                        valor_por_kg=Decimal('7.00'),
                        peso_medio_kg=Decimal('350.00'),
                        observacao=f'Venda de 20% das nulíparas (descarte) - Estoque disponível: {estoque_nuliparas}'
                    )
                    vendas.append({'categoria': cat_nulipara.nome, 'quantidade': vendas_nuliparas})
        
        return vendas

    def _processar_transferencias(self, propriedade, data, saldos, categorias, ano,
                                   invernada_grande, favo_mel, girassol):
        """Processa descarte: 20% das vacas em reprodução → descarte → VENDER na própria fazenda - SEMPRE verifica estoque
        
        REGRA ATUALIZADA: Vacas descarte são VENDIDAS na fazenda Canta Galo a R$ 3.500,00 por animal
        ao invés de serem transferidas para outras fazendas.
        """
        transferencias = []
        
        cat_vaca_reproducao = categorias.get('vaca_reproducao')
        cat_vaca_descarte = categorias.get('vaca_descarte')
        
        if not cat_vaca_reproducao:
            return transferencias
        
        estoque_vacas_reproducao = saldos.get(cat_vaca_reproducao.nome, 0)
        if estoque_vacas_reproducao == 0:
            return transferencias
        
        # Descarte: 20% das vacas em reprodução
        descarte_quantidade_calc = int(estoque_vacas_reproducao * Decimal('0.20'))
        # CRÍTICO: Verificar se há estoque suficiente - NUNCA deixar negativo
        descarte_quantidade = min(descarte_quantidade_calc, estoque_vacas_reproducao)
        
        if descarte_quantidade == 0:
            return transferencias
        
        # Criar movimentação de descarte
        MovimentacaoProjetada.objects.create(
            propriedade=propriedade,
            categoria=cat_vaca_reproducao,
            data_movimentacao=data,
            tipo_movimentacao='PROMOCAO_SAIDA',
            quantidade=descarte_quantidade,
            observacao=f'Descarte de 20% das vacas em reprodução - Estoque disponível: {estoque_vacas_reproducao}'
        )
        
        if cat_vaca_descarte:
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                categoria=cat_vaca_descarte,
                data_movimentacao=data,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                quantidade=descarte_quantidade,
                observacao=f'Descarte de 20% das vacas em reprodução - Estoque disponível: {estoque_vacas_reproducao}'
            )
        
        # ========================================================================
        # REGRA ATUALIZADA - CONFIGURAÇÃO PADRÃO CANTA GALO:
        # VACAS DESCARTE SÃO VENDIDAS NA PRÓPRIA FAZENDA
        # Valor: R$ 3.500,00 por animal
        # Esta regra substitui a transferência para outras fazendas
        # ========================================================================
        # CRÍTICO: Calcular saldo REAL de descarte após a promoção criada acima
        # Usar a função que calcula o saldo considerando todas as movimentações
        saldos_reais = calcular_rebanho_por_movimentacoes(propriedade, data)
        estoque_descarte_real = saldos_reais.get(cat_vaca_descarte.nome if cat_vaca_descarte else cat_vaca_reproducao.nome, 0)
        
        # REGRA SIMPLES: NÃO VENDER SE SALDO FOR NEGATIVO OU ZERO
        if estoque_descarte_real <= 0:
            return transferencias
        
        # Só vender se houver saldo disponível (não pode ser negativo)
        quantidade_vender_descarte = min(descarte_quantidade, estoque_descarte_real)
        
        # IMPORTANTE: Se não há saldo suficiente, não vender
        if quantidade_vender_descarte <= 0:
            return transferencias
        
        # VENDER vacas descarte na própria fazenda Canta Galo
        # Valor: R$ 3.500,00 por animal
        categoria_venda = cat_vaca_descarte or cat_vaca_reproducao
        
        # Obter peso médio da categoria (padrão: 450 kg para vacas descarte)
        peso_medio_kg = Decimal('450.00')
        if categoria_venda and categoria_venda.peso_medio_kg:
            peso_medio_kg = categoria_venda.peso_medio_kg
        
        # Calcular valor por kg baseado no valor por animal (R$ 3.500,00)
        valor_por_animal = Decimal('3500.00')
        valor_por_kg = valor_por_animal / peso_medio_kg if peso_medio_kg > 0 else Decimal('7.78')
        
        # Criar venda das vacas descarte
        self._criar_venda(
            propriedade=propriedade,
            categoria=categoria_venda,
            quantidade=quantidade_vender_descarte,
            data_venda=data,
            cliente_nome='Venda de Vacas Descarte',
            valor_por_kg=valor_por_kg,
            peso_medio_kg=peso_medio_kg,
            observacao=f'Venda de vacas de descarte - {quantidade_vender_descarte} cabeças a R$ {valor_por_animal:,.2f} por animal - Estoque disponível: {estoque_descarte_real}'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'  [VENDA DESCARTE] {quantidade_vender_descarte} vacas descarte vendidas a R$ {valor_por_animal:,.2f} por animal (Total: R$ {valor_por_animal * Decimal(str(quantidade_vender_descarte)):,.2f})'
            )
        )
        
        # Transferir machos 12-24 para Favo de Mel
        # IMPORTANTE: Transferir apenas os que foram gerados no ano anterior (que evoluíram de bezerros)
        cat_macho_12_24 = categorias.get('macho_12_24')
        if cat_macho_12_24 and favo_mel:
            # Buscar machos 12-24 que evoluíram no ano anterior
            machos_gerados_ano_anterior = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                categoria=cat_macho_12_24,
                data_movimentacao__year=ano - 1
            ).aggregate(total=Sum('quantidade'))['total'] or 0
            
            if machos_gerados_ano_anterior > 0:
                # CRÍTICO: Verificar estoque disponível - NUNCA deixar negativo
                estoque_machos = saldos.get(cat_macho_12_24.nome, 0)
                quantidade_transferir = min(machos_gerados_ano_anterior, estoque_machos)
                
                if quantidade_transferir > 0:
                    self._criar_transferencia(
                        origem=propriedade,
                        destino=favo_mel,
                        categoria=cat_macho_12_24,
                        quantidade=quantidade_transferir,
                        data=data,
                        observacao=f'Transferência de machos 12-24 para recria (gerados em {ano-1}) - Estoque disponível: {estoque_machos}'
                    )
                    transferencias.append({'categoria': cat_macho_12_24.nome, 'quantidade': quantidade_transferir})
        
        return transferencias

    def _processar_invernada_grande(self, propriedade, data, categorias, ano, saldos=None):
        """Processa vendas na Invernada Grande: lotes de 60 a cada 2 meses - SEMPRE verifica estoque"""
        if ano > 2023:
            return
        
        # Buscar estoque de vacas descarte/gordas
        cat_vaca_gorda = categorias.get('vaca_gorda')
        if not cat_vaca_gorda:
            return
        
        # Verificar se é mês de venda (a cada 2 meses, começando em março)
        if data.month % 2 == 1 and data.month >= 3:  # Março, maio, julho, setembro, novembro
            # IMPORTANTE: Verificar estoque disponível antes de criar venda
            quantidade_desejada = 60
            estoque_disponivel = 0
            
            if saldos:
                # Buscar estoque da categoria de vaca gorda
                categoria_nome = cat_vaca_gorda.nome if hasattr(cat_vaca_gorda, 'nome') else str(cat_vaca_gorda)
                estoque_disponivel = saldos.get(categoria_nome, 0)
            else:
                # Se não foram fornecidos saldos, calcular baseado em movimentações
                saldos_calculados = calcular_rebanho_por_movimentacoes(propriedade, data)
                categoria_nome = cat_vaca_gorda.nome if hasattr(cat_vaca_gorda, 'nome') else str(cat_vaca_gorda)
                estoque_disponivel = saldos_calculados.get(categoria_nome, 0)
            
            # IMPORTANTE: Não vender se não houver estoque suficiente
            if estoque_disponivel <= 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [AVISO] Sem estoque disponível para venda na Invernada Grande. '
                        f'Categoria: {categoria_nome}, Estoque: {estoque_disponivel}'
                    )
                )
                return
            
            # Limitar quantidade de venda ao estoque disponível
            quantidade_venda = min(quantidade_desejada, estoque_disponivel)
            
            if quantidade_venda > 0:
                self._criar_venda(
                    propriedade=propriedade,
                    categoria=cat_vaca_gorda,
                    quantidade=quantidade_venda,
                    data_venda=data,
                    cliente_nome='JBS',
                    valor_por_kg=Decimal('6.50'),
                    peso_medio_kg=Decimal('450.00'),
                    observacao=f'Venda de vacas gordas para JBS (lote de {quantidade_venda} - estoque disponível: {estoque_disponivel})'
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [OK] Vendidas {quantidade_venda} vacas gordas para JBS em {data.strftime("%d/%m/%Y")} '
                        f'(Estoque disponível: {estoque_disponivel})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [AVISO] Não foi possível criar venda na Invernada Grande. '
                        f'Estoque insuficiente: {estoque_disponivel}'
                    )
                )

    def _processar_favo_mel(self, propriedade, data, categorias, ano, saldos):
        """Processa transferências e vendas no Favo de Mel - SEMPRE verifica estoque"""
        if ano < 2024:
            return
        
        # Transferir machos 12-24 para Girassol a cada 90 dias (lotes de 480)
        # CONFIGURAÇÃO PADRÃO: 480 cabeças a cada 90 dias, respeitando saldo disponível
        cat_macho_12_24 = categorias.get('macho_12_24')
        girassol = Propriedade.objects.filter(nome_propriedade__icontains='Girassol').first()
        
        if cat_macho_12_24 and girassol:
            # Verificar se é mês de transferência (a cada 3 meses, começando em abril)
            if data.month in [4, 7, 10] and data.day == 15:
                # CRÍTICO: Verificar estoque disponível - NUNCA deixar negativo
                estoque_machos = saldos.get(cat_macho_12_24.nome, 0)
                # CONFIGURAÇÃO PADRÃO: 480 cabeças (alterado de 300 para 480)
                quantidade_transferir = min(480, estoque_machos)
                
                if quantidade_transferir > 0:
                    self._criar_transferencia(
                        origem=propriedade,
                        destino=girassol,
                        categoria=cat_macho_12_24,
                        quantidade=quantidade_transferir,
                        data=data,
                        observacao=f'Transferência de machos 12-24 para engorda em Girassol (lote de {quantidade_transferir}) - Estoque disponível: {estoque_machos} - CONFIGURACAO PADRAO: 480 a cada 90 dias'
                    )
        
        # Vender vacas gordas a cada 3 meses (lotes de 100)
        cat_vaca_gorda = categorias.get('vaca_gorda')
        if cat_vaca_gorda:
            if data.month in [4, 7, 10] and data.day == 15:
                # CRÍTICO: Verificar estoque disponível - NUNCA deixar negativo
                estoque_vacas_gordas = saldos.get(cat_vaca_gorda.nome, 0)
                quantidade_venda = min(100, estoque_vacas_gordas)
                
                if quantidade_venda > 0:
                    self._criar_venda(
                        propriedade=propriedade,
                        categoria=cat_vaca_gorda,
                        quantidade=quantidade_venda,
                        data_venda=data,
                        cliente_nome='Frigorífico',
                        valor_por_kg=Decimal('6.50'),
                        peso_medio_kg=Decimal('450.00'),
                        observacao=f'Venda de vacas gordas após 3 meses (lote de {quantidade_venda}) - Estoque disponível: {estoque_vacas_gordas}'
                    )

    def _processar_girassol(self, propriedade, data, categorias, ano, saldos):
        """Processa engorda e vendas no Girassol: vender a cada 90 dias - SEMPRE verifica estoque"""
        cat_macho_12_24 = categorias.get('macho_12_24')
        cat_boi_gordo = categorias.get('boi_gordo_24_36')
        
        if not cat_macho_12_24 or not cat_boi_gordo:
            return
        
        # Evoluir machos 12-24 para boi gordo 24-36 após 90 dias
        # Por simplicidade, vamos processar vendas a cada 90 dias
        # Na prática, calcularia baseado em transferências recebidas
        
        # Verificar se é data de venda (a cada 90 dias aproximadamente)
        # Simplificado: vender em meses específicos após receber transferências
        if data.month in [7, 10] and data.day == 15:  # Aproximadamente 90 dias após abril e julho
            # CRÍTICO: Verificar estoque disponível - NUNCA deixar negativo
            # Primeiro verificar se há bois gordos, senão verificar machos 12-24
            estoque_bois_gordos = saldos.get(cat_boi_gordo.nome, 0)
            estoque_machos = saldos.get(cat_macho_12_24.nome, 0)
            
            # Se houver bois gordos, vender eles. Senão, verificar se pode evoluir machos
            # CONFIGURAÇÃO PADRÃO: 480 cabeças a cada 90 dias (alterado de 300 para 480)
            if estoque_bois_gordos > 0:
                quantidade_venda = min(480, estoque_bois_gordos)  # CONFIGURAÇÃO PADRÃO: 480
                if quantidade_venda > 0:
                    self._criar_venda(
                        propriedade=propriedade,
                        categoria=cat_boi_gordo,
                        quantidade=quantidade_venda,
                        data_venda=data,
                        cliente_nome='Frigorífico',
                        valor_por_kg=Decimal('7.00'),
                        peso_medio_kg=Decimal('500.00'),
                        observacao=f'Venda de gado gordo após 90 dias de engorda (lote de {quantidade_venda}) - Estoque disponível: {estoque_bois_gordos} - CONFIGURACAO PADRAO: 480 a cada 90 dias'
                    )
            elif estoque_machos >= 480:
                # Evoluir machos para bois gordos e vender
                quantidade_evoluir = min(480, estoque_machos)  # CONFIGURAÇÃO PADRÃO: 480
                if quantidade_evoluir > 0:
                    # Criar evolução
                    MovimentacaoProjetada.objects.create(
                        propriedade=propriedade,
                        categoria=cat_macho_12_24,
                        data_movimentacao=data,
                        tipo_movimentacao='PROMOCAO_SAIDA',
                        quantidade=quantidade_evoluir,
                        observacao=f'Evolução: Machos 12-24 → Bois Gordos 24-36 (após 90 dias)'
                    )
                    MovimentacaoProjetada.objects.create(
                        propriedade=propriedade,
                        categoria=cat_boi_gordo,
                        data_movimentacao=data,
                        tipo_movimentacao='PROMOCAO_ENTRADA',
                        quantidade=quantidade_evoluir,
                        observacao=f'Evolução: Machos 12-24 → Bois Gordos 24-36 (após 90 dias)'
                    )
                    # Vender imediatamente
                    self._criar_venda(
                        propriedade=propriedade,
                        categoria=cat_boi_gordo,
                        quantidade=quantidade_evoluir,
                        data_venda=data,
                        cliente_nome='Frigorífico',
                        valor_por_kg=Decimal('7.00'),
                        peso_medio_kg=Decimal('500.00'),
                        observacao=f'Venda de gado gordo após 90 dias de engorda (lote de {quantidade_evoluir}) - Estoque disponível: {estoque_machos}'
                    )

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

