# -*- coding: utf-8 -*-
"""
Sistema de Movimentações Automáticas Inteligentes
Gera automaticamente todas as movimentações baseadas no perfil da fazenda
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from .models import MovimentacaoProjetada, CategoriaAnimal, InventarioRebanho
from .ia_identificacao_fazendas import SistemaIdentificacaoFazendas, PerfilFazenda

class SistemaMovimentacoesAutomaticas:
    """Sistema que gera automaticamente todas as movimentações pecuárias"""
    
    def __init__(self):
        self.identificador = SistemaIdentificacaoFazendas()
        
    def gerar_movimentacoes_completas(self, propriedade, parametros, inventario_inicial, anos_projecao: int, data_inicio_projecao=None) -> List[MovimentacaoProjetada]:
        """
        Gera todas as movimentações automaticamente baseadas no perfil da fazenda
        data_inicio_projecao: Data de início da projeção (padrão: data atual)
        """
        from datetime import date
        
        # Se não foi passada data de início, usar data atual
        if not data_inicio_projecao:
            data_inicio_projecao = date.today()
        
        # Obter ano inicial da projeção
        if isinstance(data_inicio_projecao, date):
            ano_inicial = data_inicio_projecao.year
        else:
            # Se for datetime, extrair o ano
            ano_inicial = data_inicio_projecao.year if hasattr(data_inicio_projecao, 'year') else date.today().year
        
        print(f"[PROJECAO] Ano inicial da projecao: {ano_inicial} (data do inventario: {data_inicio_projecao})")
        try:
            # Identificar perfil da fazenda
            identificacao = self.identificador.identificar_perfil_fazenda(inventario_inicial, parametros)
            perfil = identificacao['perfil_detectado']
            
            print(f"[PERFIL] Perfil detectado: {perfil.value}")
            print(f"[ESTRATEGIAS] Estrategias: {identificacao['estrategias']}")
        except Exception as e:
            print(f"[ERRO] Erro ao identificar perfil da fazenda: {e}")
            # Usar perfil padrão em caso de erro
            perfil = PerfilFazenda.CICLO_COMPLETO
            identificacao = {
                'perfil_detectado': perfil,
                'estrategias': {
                    'vendas': {},
                    'compras': {}
                }
            }
            print(f"[PERFIL] Usando perfil padrao: {perfil.value}")
        
        # NÃO limpar movimentações aqui - isso será feito na função gerar_projecao
        # MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
        
        movimentacoes = []
        
        # Gerar movimentações para cada ano
        for ano in range(anos_projecao):
            ano_atual = ano_inicial + ano
            print(f"\n[PROJECAO] Processando ano {ano_atual}...")
            
            # Calcular saldos iniciais para o ano
            saldos_iniciais_ano = self._calcular_saldos_iniciais_ano(ano, inventario_inicial, movimentacoes, ano_inicial)
            
            # IMPORTANTE: Para cálculo de nascimentos, usar o saldo INICIAL de matrizes do ano
            # A taxa de natalidade (ex: 70%) se refere ao número de matrizes no início do ano
            # Não usar saldo médio, pois isso reduziria incorretamente o número de nascimentos
            
            # Gerar movimentações mensais
            saldos_iniciais_mes = saldos_iniciais_ano.copy()
            for mes in range(1, 13):
                data_referencia = datetime(ano_atual, mes, 15)
                data_final_mes = datetime(ano_atual, mes, 28)  # Último dia do mês
                print(f"  [MES] Mes {mes:02d}/{ano_atual}")
                print(f"    [SALDO] Saldo inicial do mes: {dict(saldos_iniciais_mes)}")
                
                # 1. NASCIMENTOS (apenas nos meses de estação: julho a dezembro)
                # A taxa de natalidade anual (ex: 70%) significa que 70% das matrizes iniciais devem parir durante a estação
                # Estação de nascimentos: julho (7), agosto (8), setembro (9), outubro (10), novembro (11), dezembro (12)
                nascimentos = []
                descartes_matrizes = []
                if mes in [7, 8, 9, 10, 11, 12]:  # Estação de nascimentos
                    nascimentos = self._gerar_nascimentos_estacao(propriedade, data_referencia, saldos_iniciais_ano, parametros, perfil, mes)
                    movimentacoes.extend(nascimentos)
                    
                    # Gerar descarte de matrizes que não pariram (20% das matrizes)
                    # Apenas no primeiro mês da estação (julho) para evitar duplicação
                    if mes == 7:
                        descartes_matrizes = self._gerar_descarte_matrizes(propriedade, data_referencia, saldos_iniciais_ano, parametros)
                        movimentacoes.extend(descartes_matrizes)
                        
                        # Vender 20% das primíparas que não ficaram prenhas
                        vendas_primiparas = self._gerar_vendas_primiparas_nao_prenhas(propriedade, data_referencia, saldos_iniciais_ano)
                        movimentacoes.extend(vendas_primiparas)
                
                # 10% das matrizes ficam na fazenda para nova chance (não precisa criar movimentação, apenas não descartar)
                
                # 2. MORTES (baseado em mortalidade)
                mortes = self._gerar_mortes(propriedade, data_referencia, saldos_iniciais_mes, parametros)
                movimentacoes.extend(mortes)
                
                # 3. CALCULAR SALDO APÓS NASCIMENTOS E MORTES (para evolução)
                saldo_pos_nascimentos_mortes = self._calcular_saldo_final(saldos_iniciais_mes, nascimentos, mortes, [], [], [], [])
                
                # 4. EVOLUÇÃO DE IDADE (PROMOÇÃO) - ANTES DAS VENDAS!
                # Usar data_referencia (meio do mês) para que a evolução aconteça antes das vendas
                promocoes = self._gerar_evolucao_idade(propriedade, data_referencia, saldo_pos_nascimentos_mortes, perfil)
                movimentacoes.extend(promocoes)
                
                # 5. CALCULAR SALDO APÓS EVOLUÇÃO (para vendas e compras)
                saldo_pos_evolucao = self._calcular_saldo_final(saldo_pos_nascimentos_mortes, [], [], [], [], [], promocoes)
                
                # 6. VENDAS (baseado no perfil) - AGORA COM ANIMAIS JÁ EVOLUÍDOS
                # IMPORTANTE: Não vender animais recém-nascidos no mesmo ano
                # Passar nascimentos do ano para excluir da venda
                # IMPORTANTE: Passar saldo inicial do ano para calcular percentual sobre animais do ano anterior
                nascimentos_ano = [n for n in movimentacoes if n.tipo_movimentacao == 'NASCIMENTO' and n.data_movimentacao.year == ano_atual]
                vendas = self._gerar_vendas_automaticas(propriedade, data_referencia, saldo_pos_evolucao, perfil, identificacao['estrategias'], nascimentos_ano, ano_atual, saldos_iniciais_ano)
                movimentacoes.extend(vendas)
                
                # 7. COMPRAS (baseado no perfil)
                compras = self._gerar_compras_automaticas(propriedade, data_referencia, saldo_pos_evolucao, perfil, identificacao['estrategias'])
                movimentacoes.extend(compras)
                
                # 8. TRANSFERÊNCIAS (entre fazendas do mesmo produtor)
                # IMPORTANTE: Transferências apenas no início do ano (janeiro)
                # CRÍTICO: Usar saldo APÓS promoções (saldo_pos_evolucao) para considerar saldo real disponível
                transferencias = []
                if mes == 1:  # Apenas em janeiro de cada ano
                    # Passar saldo após promoções para verificar saldo real disponível
                    transferencias = self._gerar_transferencias_automaticas(propriedade, data_referencia, saldo_pos_evolucao, perfil, ano_atual)
                movimentacoes.extend(transferencias)
                
                # 9. CALCULAR SALDO FINAL APÓS TODAS AS MOVIMENTAÇÕES
                saldo_final = self._calcular_saldo_final(saldo_pos_evolucao, [], [], vendas, compras, transferencias, [])
                
                print(f"    [SALDO] Saldo final do mes: {dict(saldo_final)}")
                
                # Atualizar saldos para o próximo mês (após todas as movimentações)
                saldos_iniciais_mes = saldo_final
        
        print(f"\n[SUCESSO] Total de movimentacoes geradas: {len(movimentacoes)}")
        return movimentacoes
    
    def _calcular_saldo_medio_matrizes_ano(self, ano_atual: int, saldos_iniciais_ano: Dict[str, int], movimentacoes: List[MovimentacaoProjetada], parametros) -> Dict[str, int]:
        """
        Calcula saldo médio de matrizes ao longo do ano para cálculo mais preciso de nascimentos.
        Considera que as matrizes podem mudar (mortes, vendas) ao longo do ano.
        """
        # Começar com saldo inicial
        saldo_medio = saldos_iniciais_ano.copy()
        
        # Contar matrizes no saldo inicial
        matrizes_inicial = 0
        for categoria, quantidade in saldos_iniciais_ano.items():
            categoria_lower = categoria.lower()
            if any(termo in categoria_lower for termo in ['vaca', 'multípara', 'primípara']) and any(termo in categoria_lower for termo in ['reprodução', 'reproducao', '36', '+36']):
                matrizes_inicial += quantidade
        
        # Calcular saldo final estimado (considerando mortalidade e vendas típicas)
        # Taxa de mortalidade de adultos aplicada às matrizes
        taxa_mortalidade_adultos = parametros.taxa_mortalidade_adultos_anual / 100
        # Estimativa de vendas de matrizes (normalmente baixa, ~5-10%)
        taxa_venda_matrizes = 0.05  # 5% estimado
        
        # Saldo final estimado de matrizes
        matrizes_final_estimado = matrizes_inicial * (1 - taxa_mortalidade_adultos - taxa_venda_matrizes)
        
        # Saldo médio = média entre inicial e final estimado
        matrizes_medio = int((matrizes_inicial + matrizes_final_estimado) / 2)
        
        # Atualizar saldo médio apenas para categorias de matrizes
        for categoria, quantidade in saldos_iniciais_ano.items():
            categoria_lower = categoria.lower()
            if any(termo in categoria_lower for termo in ['vaca', 'multípara', 'primípara']) and any(termo in categoria_lower for termo in ['reprodução', 'reproducao', '36', '+36']):
                # Proporcionalmente ajustar
                if matrizes_inicial > 0:
                    proporcao = quantidade / matrizes_inicial
                    saldo_medio[categoria] = int(matrizes_medio * proporcao)
        
        print(f"    [SALDO] Saldo medio de matrizes para o ano {ano_atual}: {matrizes_medio} (inicial: {matrizes_inicial}, final estimado: {int(matrizes_final_estimado)})")
        return saldo_medio
    
    def _calcular_saldos_iniciais_ano(self, ano: int, inventario_inicial: List[InventarioRebanho], movimentacoes_anteriores: List[MovimentacaoProjetada], ano_inicial: int = None) -> Dict[str, int]:
        """Calcula saldos iniciais para o ano baseado no inventário e movimentações anteriores"""
        if ano == 0:
            # Primeiro ano: usar inventário inicial
            saldos = {}
            for item in inventario_inicial:
                saldos[item.categoria.nome] = item.quantidade
            return saldos
        else:
            # Anos seguintes: calcular baseado nas movimentações do ano anterior
            return self._calcular_saldos_finais_ano_anterior(movimentacoes_anteriores, ano, ano_inicial)
    
    def _calcular_saldos_finais_ano_anterior(self, movimentacoes: List[MovimentacaoProjetada], ano_atual: int, ano_inicial: int = None) -> Dict[str, int]:
        """Calcula saldos finais do ano anterior"""
        if ano_inicial is None:
            ano_inicial = datetime.now().year
        ano_anterior = ano_inicial + ano_atual - 1
        
        # Verificar se há movimentações
        if not movimentacoes:
            return {}
        
        # Começar com saldos iniciais do ano anterior
        from .models import InventarioRebanho
        propriedade = movimentacoes[0].propriedade
        
        # Inicializar saldos com o inventário inicial
        saldos = defaultdict(int)
        inventario_items = InventarioRebanho.objects.filter(propriedade=propriedade)
        for item in inventario_items:
            saldos[item.categoria.nome] = item.quantidade
        
        # Aplicar todas as movimentações até o final do ano anterior
        for mov in movimentacoes:
            if mov.data_movimentacao.year <= ano_anterior:
                categoria = mov.categoria.nome
                
                if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
                    saldos[categoria] += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
                    saldos[categoria] -= mov.quantidade
        
        print(f"  [SALDOS] Saldos calculados para ano {ano_atual} (baseado no ano {ano_anterior}): {dict(saldos)}")
        return dict(saldos)
    
    def _gerar_nascimentos_estacao(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], parametros, perfil: PerfilFazenda, mes: int) -> List[MovimentacaoProjetada]:
        """
        Gera nascimentos apenas na estação de nascimentos (julho a dezembro).
        Distribui 70% das matrizes parindo ao longo dos 6 meses da estação.
        """
        nascimentos = []
        
        # Meses da estação: julho (7), agosto (8), setembro (9), outubro (10), novembro (11), dezembro (12)
        meses_estacao = [7, 8, 9, 10, 11, 12]
        
        if mes not in meses_estacao:
            return nascimentos
        
        # Buscar matrizes - IMPORTANTE: 
        # - "Vacas em Reprodução +36 M" são todas matrizes
        # - 80% das Primíparas estão em reprodução (são matrizes)
        # - 20% das Primíparas são vendidas (não ficaram prenhas)
        matrizes = 0
        categorias_matrizes = []
        primiparas_total = 0
        
        # Tentar nomes novos primeiro - Vacas em reprodução (+36 meses)
        if 'Vacas em Reprodução +36 M' in saldos_iniciais:
            qtd = saldos_iniciais['Vacas em Reprodução +36 M']
            matrizes += qtd
            if qtd > 0:
                categorias_matrizes.append(('Vacas em Reprodução +36 M', qtd))
        
        # Primíparas: 80% estão em reprodução (são matrizes)
        if 'Primíparas 24-36 M' in saldos_iniciais:
            primiparas_total = saldos_iniciais['Primíparas 24-36 M']
            primiparas_reproducao = int(primiparas_total * 0.80)  # 80% em reprodução
            matrizes += primiparas_reproducao
            if primiparas_reproducao > 0:
                categorias_matrizes.append(('Primíparas 24-36 M (80% em reprodução)', primiparas_reproducao))
        
        # Tentar nomes antigos como fallback
        if matrizes == 0:
            if 'Multíparas (>36m)' in saldos_iniciais:
                qtd = saldos_iniciais['Multíparas (>36m)']
                matrizes += qtd
                if qtd > 0:
                    categorias_matrizes.append(('Multíparas (>36m)', qtd))
            
            if 'Primíparas (24-36m)' in saldos_iniciais:
                primiparas_total = saldos_iniciais['Primíparas (24-36m)']
                primiparas_reproducao = int(primiparas_total * 0.80)  # 80% em reprodução
                matrizes += primiparas_reproducao
                if primiparas_reproducao > 0:
                    categorias_matrizes.append(('Primíparas (24-36m) (80% em reprodução)', primiparas_reproducao))
        
        # Buscar também por termos parciais (mais flexível)
        if matrizes == 0:
            for categoria_nome, quantidade in saldos_iniciais.items():
                if quantidade > 0:
                    categoria_lower = categoria_nome.lower()
                    # Vacas/multíparas com +36 meses
                    if any(termo in categoria_lower for termo in ['vaca', 'multípara']) and any(termo in categoria_lower for termo in ['reprodução', 'reproducao', '+36', '36 m']):
                        if 'primípara' not in categoria_lower and 'primipara' not in categoria_lower:
                            matrizes += quantidade
                            categorias_matrizes.append((categoria_nome, quantidade))
                    # Primíparas: 80% em reprodução
                    elif 'primípara' in categoria_lower or 'primipara' in categoria_lower:
                        primiparas_reproducao = int(quantidade * 0.80)  # 80% em reprodução
                        matrizes += primiparas_reproducao
                        if primiparas_reproducao > 0:
                            categorias_matrizes.append((f'{categoria_nome} (80% em reprodução)', primiparas_reproducao))
        
        # Exibir informações sobre matrizes encontradas
        if categorias_matrizes:
            print(f"    [MATRIZES] Matrizes encontradas por categoria:")
            for cat, qtd in categorias_matrizes:
                print(f"       - {cat}: {qtd}")
        
        print(f"    [MATRIZES] Total de matrizes encontradas: {matrizes}")
        
        if matrizes > 0:
            # Calcular nascimentos baseado na natalidade
            # A taxa de natalidade anual (ex: 70%) significa que 70% das matrizes devem parir durante a estação
            # Distribuímos os 70% ao longo dos 6 meses da estação (julho a dezembro)
            taxa_natalidade_anual = float(parametros.taxa_natalidade_anual)
            
            # Total de nascimentos na estação = 70% das matrizes
            total_nascimentos_estacao = int(matrizes * taxa_natalidade_anual / 100)
            
            # Distribuir igualmente pelos 6 meses da estação
            nascimentos_por_mes = total_nascimentos_estacao // 6
            resto_nascimentos = total_nascimentos_estacao % 6
            
            # No primeiro mês (julho), adicionar o resto para garantir que o total seja exato
            posicao_mes_estacao = meses_estacao.index(mes)
            if posicao_mes_estacao == 0:
                total_nascimentos = nascimentos_por_mes + resto_nascimentos
            else:
                total_nascimentos = nascimentos_por_mes
            
            print(f"    [NATALIDADE] Taxa de natalidade anual: {taxa_natalidade_anual}%")
            print(f"    [MATRIZES] Matrizes disponiveis: {matrizes}")
            print(f"    [NASCIMENTOS] Total de nascimentos na estacao (70% das matrizes): {total_nascimentos_estacao}")
            print(f"    [NASCIMENTOS] Nascimentos calculados para este mes ({mes}): {total_nascimentos}")
            print(f"    [NASCIMENTOS] Distribuicao: {nascimentos_por_mes} por mes + {resto_nascimentos} no primeiro mes")
            
            if total_nascimentos > 0:
                # Distribuir nascimentos entre bezerros e bezerras (50/50)
                bezerros = total_nascimentos // 2
                bezerras = total_nascimentos - bezerros
                
                try:
                    # Tentar nomes novos primeiro
                    try:
                        categoria_bezerros = CategoriaAnimal.objects.get(nome='Bezerro(o) 0-12 M')
                    except CategoriaAnimal.DoesNotExist:
                        categoria_bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
                    
                    try:
                        categoria_bezerras = CategoriaAnimal.objects.get(nome='Bezerro(a) 0-12 F')
                    except CategoriaAnimal.DoesNotExist:
                        categoria_bezerras = CategoriaAnimal.objects.get(nome='Bezerras (0-12m)')
                    
                    if bezerros > 0:
                        nascimentos.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='NASCIMENTO',
                            categoria=categoria_bezerros,
                            quantidade=bezerros,
                            observacao=f'Nascimentos automáticos - {bezerros} bezerros (Natalidade: {parametros.taxa_natalidade_anual}%)'
                        ))
                    
                    if bezerras > 0:
                        nascimentos.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='NASCIMENTO',
                            categoria=categoria_bezerras,
                            quantidade=bezerras,
                            observacao=f'Nascimentos automáticos - {bezerras} bezerras (Natalidade: {parametros.taxa_natalidade_anual}%)'
                        ))
                    
                    print(f"    [NASCIMENTOS] Nascimentos: {bezerros} bezerros + {bezerras} bezerras = {total_nascimentos}")
                    
                except CategoriaAnimal.DoesNotExist:
                    print("    [AVISO] Categorias de bezerros nao encontradas")
        else:
            print(f"    [AVISO] Nenhuma matriz encontrada para gerar nascimentos. Saldos disponiveis: {list(saldos_iniciais.keys())}")
        
        return nascimentos
    
    def _gerar_descarte_matrizes(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], parametros) -> List[MovimentacaoProjetada]:
        """
        Gera descarte de 20% das matrizes que não pariram.
        Apenas no início da estação (julho).
        """
        from .models import CategoriaAnimal
        
        descartes = []
        
        # Buscar matrizes - IMPORTANTE: Apenas "Vacas em Reprodução +36 M" são consideradas matrizes
        # Primíparas não são contadas como matrizes para descarte
        matrizes = 0
        categorias_matrizes_dict = {}  # {nome_categoria: quantidade}
        
        # Tentar nomes novos primeiro - APENAS vacas em reprodução (+36 meses)
        if 'Vacas em Reprodução +36 M' in saldos_iniciais:
            qtd = saldos_iniciais['Vacas em Reprodução +36 M']
            matrizes += qtd
            if qtd > 0:
                categorias_matrizes_dict['Vacas em Reprodução +36 M'] = qtd
        
        # Tentar nomes antigos como fallback - APENAS multíparas
        if matrizes == 0:
            if 'Multíparas (>36m)' in saldos_iniciais:
                qtd = saldos_iniciais['Multíparas (>36m)']
                matrizes += qtd
                if qtd > 0:
                    categorias_matrizes_dict['Multíparas (>36m)'] = qtd
        
        # Buscar também por termos parciais (mais flexível) - APENAS vacas/multíparas +36 meses
        if matrizes == 0:
            for categoria_nome, quantidade in saldos_iniciais.items():
                if quantidade > 0:
                    categoria_lower = categoria_nome.lower()
                    # IMPORTANTE: Apenas contar vacas/multíparas com +36 meses (não primíparas)
                    if any(termo in categoria_lower for termo in ['vaca', 'multípara']) and any(termo in categoria_lower for termo in ['reprodução', 'reproducao', '+36', '36 m']):
                        # Excluir primíparas explicitamente
                        if 'primípara' not in categoria_lower and 'primipara' not in categoria_lower:
                            matrizes += quantidade
                            categorias_matrizes_dict[categoria_nome] = quantidade
        
        if matrizes == 0:
            print(f"    [AVISO] Nenhuma matriz encontrada para descarte. Saldos disponiveis: {list(saldos_iniciais.keys())}")
            return descartes
        
        # Calcular descarte: 20% das matrizes
        total_descarte = int(matrizes * 0.20)
        
        # IMPORTANTE: Validar estoque - não vender mais do que está disponível
        total_descarte = min(total_descarte, matrizes)
        
        print(f"    [MATRIZES] Total de matrizes: {matrizes}")
        print(f"    [DESCARTE] Descarte calculado (20% das matrizes): {total_descarte}")
        print(f"    [MATRIZES] Matrizes que ficam (70% pariram + 10% nova chance): {matrizes - total_descarte}")
        
        if total_descarte > 0:
            # Distribuir descarte proporcionalmente entre as categorias de matrizes
            for categoria_nome, quantidade_categoria in categorias_matrizes_dict.items():
                if quantidade_categoria > 0:
                    # Proporção desta categoria no total de matrizes
                    proporcao = quantidade_categoria / matrizes
                    descarte_categoria = int(total_descarte * proporcao)
                    
                    # Garantir pelo menos 1 se houver matrizes e descarte total > 0
                    if descarte_categoria == 0 and total_descarte > 0 and quantidade_categoria > 0:
                        descarte_categoria = 1
                    
                    if descarte_categoria > 0 and descarte_categoria <= quantidade_categoria:
                        try:
                            categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                            
                            # Buscar categoria de descarte ou usar a mesma categoria
                            try:
                                categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Descarte')
                            except CategoriaAnimal.DoesNotExist:
                                categoria_descarte = categoria_obj
                            
                            descartes.append(MovimentacaoProjetada(
                                propriedade=propriedade,
                                data_movimentacao=data_referencia,
                                tipo_movimentacao='VENDA',
                                categoria=categoria_obj,
                                quantidade=descarte_categoria,
                                observacao=f'Descarte de matrizes (20% do rebanho) - {descarte_categoria} de {categoria_nome}'
                            ))
                            
                            print(f"    [DESCARTE] Descarte: {descarte_categoria} {categoria_nome}")
                        except CategoriaAnimal.DoesNotExist:
                            print(f"    [AVISO] Categoria '{categoria_nome}' nao encontrada para descarte")
        
        return descartes
    
    def _gerar_vendas_primiparas_nao_prenhas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int]) -> List[MovimentacaoProjetada]:
        """
        Gera vendas de 20% das primíparas que não ficaram prenhas.
        Apenas no início da estação (julho).
        """
        from .models import CategoriaAnimal, InventarioRebanho
        
        vendas = []
        
        # Buscar primíparas
        primiparas_total = 0
        categoria_primiparas = None
        
        # Tentar nomes novos primeiro
        if 'Primíparas 24-36 M' in saldos_iniciais:
            primiparas_total = saldos_iniciais['Primíparas 24-36 M']
            try:
                categoria_primiparas = CategoriaAnimal.objects.get(nome='Primíparas 24-36 M')
            except CategoriaAnimal.DoesNotExist:
                pass
        
        # Tentar nomes antigos como fallback
        if primiparas_total == 0:
            if 'Primíparas (24-36m)' in saldos_iniciais:
                primiparas_total = saldos_iniciais['Primíparas (24-36m)']
                try:
                    categoria_primiparas = CategoriaAnimal.objects.get(nome='Primíparas (24-36m)')
                except CategoriaAnimal.DoesNotExist:
                    pass
        
        # Buscar também por termos parciais
        if primiparas_total == 0:
            for categoria_nome, quantidade in saldos_iniciais.items():
                if quantidade > 0:
                    categoria_lower = categoria_nome.lower()
                    if ('primípara' in categoria_lower or 'primipara' in categoria_lower) and ('24' in categoria_nome or '36' in categoria_nome):
                        primiparas_total = quantidade
                        try:
                            categoria_primiparas = CategoriaAnimal.objects.get(nome=categoria_nome)
                            break
                        except CategoriaAnimal.DoesNotExist:
                            pass
        
        if primiparas_total == 0 or not categoria_primiparas:
            print(f"    [AVISO] Nenhuma primipara encontrada para venda. Saldos disponiveis: {list(saldos_iniciais.keys())}")
            return vendas
        
        # Calcular venda: 20% das primíparas (as que não ficaram prenhas)
        total_venda = int(primiparas_total * 0.20)
        
        # IMPORTANTE: Validar estoque - não vender mais do que está disponível
        total_venda = min(total_venda, primiparas_total)
        
        print(f"    [PRIMIPARAS] Total de primiparas: {primiparas_total}")
        print(f"    [VENDA] Venda de primiparas nao prenhas (20%): {total_venda}")
        print(f"    [REPRODUCAO] Primiparas que ficam em reproducao (80%): {primiparas_total - total_venda}")
        
        if total_venda > 0:
            # Buscar valor por cabeça do inventário ou CEPEA do ano da projeção
            valor_por_cabeca = None
            try:
                ano_mov = data_referencia.year if data_referencia else None
                inventario_item = InventarioRebanho.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_primiparas
                ).first()
                if inventario_item and inventario_item.valor_por_cabeca:
                    valor_por_cabeca = inventario_item.valor_por_cabeca
                else:
                    # Usar preço CEPEA do ano da projeção
                    from gestao_rural.views import obter_valor_padrao_por_categoria
                    valor_por_cabeca = obter_valor_padrao_por_categoria(
                        categoria_primiparas, propriedade, ano_mov
                    )
            except Exception as e:
                print(f"    [ERRO] Erro ao buscar valor por cabeca: {e}")
            
            vendas.append(MovimentacaoProjetada(
                propriedade=propriedade,
                data_movimentacao=data_referencia,
                tipo_movimentacao='VENDA',
                categoria=categoria_primiparas,
                quantidade=total_venda,
                valor_por_cabeca=valor_por_cabeca,
                valor_total=valor_por_cabeca * total_venda if valor_por_cabeca else None,
                observacao=f'Venda de primíparas não prenhas (20% do total) - {total_venda} de {primiparas_total} primíparas'
            ))
            
            print(f"    [VENDA] Venda de primiparas: {total_venda} {categoria_primiparas.nome}")
        
        return vendas
    
    def _calcular_saldo_final(self, saldos_iniciais: Dict[str, int], nascimentos: List, mortes: List, vendas: List, compras: List, transferencias: List, promocoes: List = None) -> Dict[str, int]:
        """Calcula o saldo final após todas as movimentações do mês (incluindo evolução)"""
        saldo_final = saldos_iniciais.copy()
        
        # Aplicar nascimentos
        for mov in nascimentos:
            categoria = mov.categoria.nome
            saldo_final[categoria] = saldo_final.get(categoria, 0) + mov.quantidade
        
        # Aplicar mortes
        for mov in mortes:
            categoria = mov.categoria.nome
            saldo_final[categoria] = saldo_final.get(categoria, 0) - mov.quantidade
        
        # Aplicar promoções (evolução de idade) - se fornecidas
        if promocoes:
            for mov in promocoes:
                categoria = mov.categoria.nome
                if mov.tipo_movimentacao == 'PROMOCAO_ENTRADA':
                    saldo_final[categoria] = saldo_final.get(categoria, 0) + mov.quantidade
                elif mov.tipo_movimentacao == 'PROMOCAO_SAIDA':
                    saldo_final[categoria] = saldo_final.get(categoria, 0) - mov.quantidade
        
        # Aplicar vendas
        for mov in vendas:
            categoria = mov.categoria.nome
            saldo_antes = saldo_final.get(categoria, 0)
            saldo_final[categoria] = saldo_antes - mov.quantidade
            
            # IMPORTANTE: Validar se a venda não deixou saldo negativo
            if saldo_final[categoria] < 0:
                print(f"    [ERRO] Venda de {mov.quantidade} {categoria} deixaria saldo negativo! Saldo antes: {saldo_antes}, Saldo após: {saldo_final[categoria]}")
                # Ajustar quantidade de venda para não deixar negativo
                quantidade_ajustada = saldo_antes
                saldo_final[categoria] = 0
                print(f"    [AJUSTE] Quantidade de venda ajustada de {mov.quantidade} para {quantidade_ajustada} para evitar saldo negativo")
                # Atualizar a quantidade na movimentação se possível
                if hasattr(mov, 'quantidade'):
                    mov.quantidade = quantidade_ajustada
        
        # Aplicar compras
        for mov in compras:
            categoria = mov.categoria.nome
            saldo_final[categoria] = saldo_final.get(categoria, 0) + mov.quantidade
        
        # Aplicar transferências
        for mov in transferencias:
            categoria = mov.categoria.nome
            if mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                saldo_final[categoria] = saldo_final.get(categoria, 0) + mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                saldo_antes = saldo_final.get(categoria, 0)
                saldo_final[categoria] = saldo_antes - mov.quantidade
                
                # IMPORTANTE: Validar se a transferência não deixou saldo negativo
                if saldo_final[categoria] < 0:
                    print(f"    [ERRO] Transferência de {mov.quantidade} {categoria} deixaria saldo negativo! Saldo antes: {saldo_antes}, Saldo após: {saldo_final[categoria]}")
                    # Ajustar quantidade de transferência para não deixar negativo
                    quantidade_ajustada = saldo_antes
                    saldo_final[categoria] = 0
                    print(f"    [AJUSTE] Quantidade de transferência ajustada de {mov.quantidade} para {quantidade_ajustada} para evitar saldo negativo")
                    # Atualizar a quantidade na movimentação se possível
                    if hasattr(mov, 'quantidade'):
                        mov.quantidade = quantidade_ajustada
        
        # Garantir que não há saldos negativos (última verificação de segurança)
        for categoria in list(saldo_final.keys()):
            if saldo_final[categoria] < 0:
                print(f"    [AVISO] Saldo negativo detectado para {categoria}: {saldo_final[categoria]}. Ajustando para 0.")
                saldo_final[categoria] = 0
        
        return saldo_final
    
    def _gerar_evolucao_idade(self, propriedade, data_referencia: datetime, saldos_finais: Dict[str, int], perfil: PerfilFazenda) -> List[MovimentacaoProjetada]:
        """Gera evolução automática de idade dos animais - ANTES DAS VENDAS para cálculo correto"""
        promocoes = []
        print(f"    [EVOLUCAO] Processando evolucao de idade. Saldos disponiveis: {dict(saldos_finais)}")
        
        # Mapeamento de evolução de idade - tentar nomes novos e antigos
        evolucoes = [
            # Nomes novos (padrão do sistema)
            ('Bezerro(o) 0-12 M', 'Garrote 12-24 M'),
            ('Bezerro(a) 0-12 F', 'Novilha 12-24 M'),
            ('Garrote 12-24 M', 'Boi 24-36 M'),
            ('Novilha 12-24 M', 'Primíparas 24-36 M'),
            ('Primíparas 24-36 M', 'Vacas em Reprodução +36 M'),
            # Nomes antigos (fallback)
            ('Bezerros (0-12m)', 'Garrotes (12-24m)'),
            ('Bezerras (0-12m)', 'Novilhas (12-24m)'),
            ('Garrotes (12-24m)', 'Bois (24-36m)'),
            ('Novilhas (12-24m)', 'Primíparas (24-36m)'),
            ('Primíparas (24-36m)', 'Multíparas (>36m)'),
        ]
        
        for categoria_origem, categoria_destino in evolucoes:
            quantidade_origem = saldos_finais.get(categoria_origem, 0)
            
            if quantidade_origem > 0:
                # Calcular quantos animais evoluem (baseado na idade)
                taxa_evolucao = self._calcular_taxa_evolucao_idade(categoria_origem, data_referencia.month)
                quantidade_evolui = int(quantidade_origem * taxa_evolucao)
                
                if quantidade_evolui > 0:
                    try:
                        # Tentar buscar categoria origem
                        try:
                            categoria_origem_obj = CategoriaAnimal.objects.get(nome=categoria_origem, ativo=True)
                        except CategoriaAnimal.DoesNotExist:
                            # Buscar por termo parcial
                            categoria_origem_obj = CategoriaAnimal.objects.filter(
                                nome__icontains=categoria_origem.split()[0], ativo=True
                            ).first()
                            if not categoria_origem_obj:
                                continue
                        
                        # Tentar buscar categoria destino
                        try:
                            categoria_destino_obj = CategoriaAnimal.objects.get(nome=categoria_destino, ativo=True)
                        except CategoriaAnimal.DoesNotExist:
                            # Buscar por termo parcial
                            categoria_destino_obj = CategoriaAnimal.objects.filter(
                                nome__icontains=categoria_destino.split()[0], ativo=True
                            ).first()
                            if not categoria_destino_obj:
                                continue
                        
                        # Saída da categoria origem
                        promocoes.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            categoria=categoria_origem_obj,
                            quantidade=quantidade_evolui,
                            observacao=f'Evolução de idade - {quantidade_evolui} de {quantidade_origem} animais ({categoria_origem} → {categoria_destino})'
                        ))
                        
                        # Entrada na categoria destino
                        promocoes.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            categoria=categoria_destino_obj,
                            quantidade=quantidade_evolui,
                            observacao=f'Evolução de idade - {quantidade_evolui} de {quantidade_origem} animais ({categoria_origem} → {categoria_destino})'
                        ))
                        
                        print(f"    [EVOLUCAO] Evolucao: {quantidade_evolui}/{quantidade_origem} animais {categoria_origem_obj.nome} -> {categoria_destino_obj.nome}")
                        
                    except Exception as e:
                        print(f"    [ERRO] Erro ao processar evolucao de {categoria_origem} para {categoria_destino}: {e}")
        
        print(f"    [EVOLUCAO] Total de promocoes geradas: {len(promocoes)} movimentacoes")
        return promocoes
    
    def _calcular_taxa_evolucao_idade(self, categoria: str, mes: int) -> float:
        """Calcula taxa de evolução baseada na categoria e mês"""
        # Taxas baseadas na idade típica de cada categoria
        if 'Bezerro' in categoria or 'Bezerra' in categoria:
            # Bezerros evoluem em 12 meses
            return 0.083  # 1/12 por mês
        elif 'Garrotes' in categoria or 'Novilha' in categoria:
            # Garrotes e novilhas evoluem em 12 meses
            return 0.083
        elif 'Primípara' in categoria:
            # Primíparas evoluem em 12 meses
            return 0.083
        else:
            return 0.0
    
    def _gerar_mortes(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], parametros) -> List[MovimentacaoProjetada]:
        """Gera mortes baseado na mortalidade configurada"""
        mortes = []
        
        # Mortalidade mensal
        taxa_mortalidade_bezerros_mensal = parametros.taxa_mortalidade_bezerros_anual / 100 / 12
        taxa_mortalidade_adultos_mensal = parametros.taxa_mortalidade_adultos_anual / 100 / 12
        
        for categoria, quantidade in saldos_iniciais.items():
            if quantidade > 0:
                # Determinar taxa de mortalidade
                if any(termo in categoria.lower() for termo in ['bezerro', 'bezerra', '0-12']):
                    taxa_mortalidade = taxa_mortalidade_bezerros_mensal
                else:
                    taxa_mortalidade = taxa_mortalidade_adultos_mensal
                
                quantidade_mortes = int(quantidade * taxa_mortalidade)
                
                if quantidade_mortes > 0:
                    try:
                        categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                        
                        mortes.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='MORTE',
                            categoria=categoria_obj,
                            quantidade=quantidade_mortes,
                            observacao=f'Mortes automáticas - {categoria} (Taxa: {taxa_mortalidade*100:.2f}%)'
                        ))
                        
                        print(f"    [MORTES] Mortes: {quantidade_mortes} {categoria}")
                        
                    except CategoriaAnimal.DoesNotExist:
                        print(f"    [AVISO] Categoria nao encontrada: {categoria}")
        
        return mortes
    
    def _gerar_vendas_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda, estrategias: Dict[str, Any], nascimentos_ano: List = None, ano_atual: int = None, saldos_iniciais_ano: Dict[str, int] = None) -> List[MovimentacaoProjetada]:
        """
        Gera vendas automáticas baseadas nos parâmetros configurados pelo usuário.
        IMPORTANTE: Não vende animais recém-nascidos no mesmo ano.
        """
        vendas = []
        
        # Calcular quantos animais recém-nascidos existem por categoria no ano atual
        nascimentos_por_categoria = {}
        if nascimentos_ano and ano_atual:
            for nascimento in nascimentos_ano:
                if nascimento.data_movimentacao.year == ano_atual:
                    categoria_nome = nascimento.categoria.nome
                    nascimentos_por_categoria[categoria_nome] = nascimentos_por_categoria.get(categoria_nome, 0) + nascimento.quantidade
        
        # Identificar categorias de bezerros/bezerras (0-12 meses) que não devem ser vendidas no mesmo ano
        categorias_bezerros = []
        for categoria_nome in saldos_iniciais.keys():
            categoria_lower = categoria_nome.lower()
            if any(termo in categoria_lower for termo in ['bezerro', 'bezerra']) and any(termo in categoria_lower for termo in ['0-12', '0-12m', '0-12 m', '0-12m']):
                categorias_bezerros.append(categoria_nome)
        
        if categorias_bezerros and nascimentos_por_categoria:
            print(f"    [PROTECAO] Protegendo bezerros recém-nascidos da venda: {nascimentos_por_categoria}")
        
        # Buscar políticas de vendas configuradas pelo usuário
        from .models import PoliticaVendasCategoria
        politicas_vendas = PoliticaVendasCategoria.objects.filter(propriedade=propriedade)
        
        # Inicializar estratégias de vendas
        estrategias_vendas = {}
        
        # Identificar categorias que devem ser transferências (não vendas)
        categorias_transferencia = []
        for categoria_nome in saldos_iniciais.keys():
            categoria_lower = categoria_nome.lower()
            # Vacas de descarte e garrotes devem ser transferências
            if 'descarte' in categoria_lower or 'garrote' in categoria_lower:
                categorias_transferencia.append(categoria_nome)
        
        if categorias_transferencia:
            print(f"    [TRANSFERENCIA] Categorias para transferencia (nao venda): {categorias_transferencia}")
        
        if politicas_vendas.exists():
            print(f"    [VENDA] Usando politicas de vendas configuradas pelo usuario")
            mes_atual = data_referencia.month
            
            for politica in politicas_vendas:
                categoria_nome = politica.categoria.nome
                
                # IMPORTANTE: Para bezerros/bezerras, usar saldo inicial do ANO (animais do ano anterior)
                # Para outras categorias, usar saldo atual do mês
                if categoria_nome in categorias_bezerros and saldos_iniciais_ano:
                    quantidade_disponivel = saldos_iniciais_ano.get(categoria_nome, 0)
                    print(f"    [VENDA] {categoria_nome}: Usando saldo inicial do ano ({quantidade_disponivel}) para calculo de venda")
                else:
                    quantidade_disponivel = saldos_iniciais.get(categoria_nome, 0)
                
                # IMPORTANTE: Vacas de descarte e garrotes são transferências, não vendas
                if categoria_nome in categorias_transferencia:
                    print(f"    [TRANSFERENCIA] {categoria_nome} sera transferencia, nao venda")
                    continue  # Pular esta categoria - será processada como transferência
                
                # IMPORTANTE: Para bezerros/bezerras, vender apenas em MAIO (após desmame)
                # Os nascimentos de julho-dezembro do ano anterior desmamam em maio do ano atual
                if categoria_nome in categorias_bezerros:
                    # Apenas vender em maio (mês 5)
                    if mes_atual != 5:
                        print(f"    [AGUARDANDO] {categoria_nome}: Aguardando maio para venda (após desmame). Mês atual: {mes_atual}")
                        continue
                    
                    # Não vender animais recém-nascidos no mesmo ano (nascidos de julho a dezembro)
                    nascimentos_categoria = nascimentos_por_categoria.get(categoria_nome, 0)
                    if nascimentos_categoria > 0:
                        # Subtrair os nascimentos do ano da quantidade disponível para venda
                        quantidade_disponivel = max(0, quantidade_disponivel - nascimentos_categoria)
                        print(f"    [PROTECAO] Excluindo {nascimentos_categoria} bezerros recém-nascidos de {categoria_nome} da venda (disponível: {quantidade_disponivel})")
                
                # Verificar se já houve venda desta categoria neste ano (para evitar vender múltiplas vezes)
                # Para bezerros/bezerras, verificar se já foi vendido em maio
                if categoria_nome in categorias_bezerros and mes_atual != 5:
                    # Se não é maio, não vender (já foi vendido em maio ou ainda não é hora)
                    print(f"    [VENDA] {categoria_nome}: Venda de bezerros apenas em maio. Mes atual: {mes_atual}")
                    continue
                
                if quantidade_disponivel > 0 and politica.percentual_venda > 0:
                    # Calcular quantidade baseada no percentual (sobre saldo inicial do ano, excluindo nascimentos)
                    quantidade_venda = int(quantidade_disponivel * politica.percentual_venda / 100)
                    
                    # IMPORTANTE: Validar estoque - não vender mais do que está disponível
                    quantidade_venda = min(quantidade_venda, quantidade_disponivel)
                    
                    if quantidade_venda > 0:
                        # Determinar valor por cabeça
                        valor_por_cabeca = None
                        valor_total = None
                        
                        if politica.usar_valor_personalizado and politica.valor_por_cabeca_personalizado:
                            valor_por_cabeca = politica.valor_por_cabeca_personalizado
                            valor_total = quantidade_venda * valor_por_cabeca
                        else:
                            # Usar valor do inventário ou CEPEA do ano da projeção
                            ano_mov = data_referencia.year if data_referencia else None
                            inventario_item = InventarioRebanho.objects.filter(
                                propriedade=propriedade,
                                categoria=politica.categoria
                            ).first()
                            if inventario_item and inventario_item.valor_por_cabeca:
                                valor_por_cabeca = inventario_item.valor_por_cabeca
                            else:
                                # Usar preço CEPEA do ano da projeção
                                from gestao_rural.views import obter_valor_padrao_por_categoria
                                valor_por_cabeca = obter_valor_padrao_por_categoria(
                                    politica.categoria, propriedade, ano_mov
                                )
                            valor_total = quantidade_venda * valor_por_cabeca
                        
                        vendas.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='VENDA',
                            categoria=politica.categoria,
                            quantidade=quantidade_venda,
                            valor_por_cabeca=valor_por_cabeca,
                            valor_total=valor_total,
                            observacao=f'Venda configurada - {categoria_nome} ({politica.percentual_venda}% do saldo inicial do ano, excluindo nascimentos)'
                        ))
                        
                        print(f"    [VENDA] Venda configurada: {quantidade_venda} {categoria_nome} ({politica.percentual_venda}% de {quantidade_disponivel} disponiveis)")
                    else:
                        print(f"    [AVISO] Sem estoque suficiente para venda de {categoria_nome}. Disponivel: {quantidade_disponivel}, Necessario: {int(quantidade_disponivel * politica.percentual_venda / 100)}")
        else:
            # Fallback para estratégias automáticas baseadas no perfil
            print(f"    [VENDA] Usando estrategias automaticas (perfil: {perfil.value})")
            estrategias_vendas = estrategias.get('vendas', {})
        
        # Processar estratégias automáticas apenas se não houver políticas configuradas
        if not politicas_vendas.exists():
            for categoria, percentual_venda in estrategias_vendas.items():
                quantidade_disponivel = saldos_iniciais.get(categoria, 0)
                
                # IMPORTANTE: Vacas de descarte e garrotes são transferências, não vendas
                if categoria in categorias_transferencia:
                    print(f"    [TRANSFERENCIA] {categoria} sera transferencia, nao venda")
                    continue  # Pular esta categoria - será processada como transferência
                
                # IMPORTANTE: Não vender animais recém-nascidos no mesmo ano
                if categoria in categorias_bezerros:
                    nascimentos_categoria = nascimentos_por_categoria.get(categoria, 0)
                    if nascimentos_categoria > 0:
                        # Subtrair os nascimentos do ano da quantidade disponível para venda
                        quantidade_disponivel = max(0, quantidade_disponivel - nascimentos_categoria)
                        print(f"    [PROTECAO] Excluindo {nascimentos_categoria} bezerros recém-nascidos de {categoria} da venda (disponível: {quantidade_disponivel})")
                
                if quantidade_disponivel > 0:
                    # Verificar se é momento de vender (baseado na frequência)
                    if self._verificar_momento_venda(data_referencia, categoria, perfil):
                        quantidade_venda = int(quantidade_disponivel * percentual_venda)
                        
                        # IMPORTANTE: Validar estoque - não vender mais do que está disponível
                        quantidade_venda = min(quantidade_venda, quantidade_disponivel)
                        
                        if quantidade_venda > 0:
                            try:
                                categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                                
                                vendas.append(MovimentacaoProjetada(
                                    propriedade=propriedade,
                                    data_movimentacao=data_referencia,
                                    tipo_movimentacao='VENDA',
                                    categoria=categoria_obj,
                                    quantidade=quantidade_venda,
                                    observacao=f'Venda automática - {categoria} ({percentual_venda*100:.0f}% do rebanho) - Perfil: {perfil.value}'
                                ))
                                
                                print(f"    [VENDA] Venda automatica: {quantidade_venda} {categoria} ({percentual_venda*100:.0f}%)")
                                
                            except CategoriaAnimal.DoesNotExist:
                                print(f"    [AVISO] Categoria nao encontrada: {categoria}")
                        else:
                            print(f"    [AVISO] Sem estoque suficiente para venda de {categoria}. Disponivel: {quantidade_disponivel}")
        
        return vendas
    
    def _gerar_compras_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda, estrategias: Dict[str, Any]) -> List[MovimentacaoProjetada]:
        """Gera compras automáticas baseadas nos parâmetros configurados pelo usuário"""
        compras = []
        
        # Inicializar estratégias de compras
        estrategias_compras = {}
        
        # Buscar políticas de vendas configuradas pelo usuário para reposição
        from .models import PoliticaVendasCategoria
        politicas_vendas = PoliticaVendasCategoria.objects.filter(propriedade=propriedade)
        
        if politicas_vendas.exists():
            print(f"    [COMPRA] Usando politicas de compras configuradas pelo usuario")
            for politica in politicas_vendas:
                if politica.reposicao_tipo in ['COMPRA', 'AMBOS'] and politica.quantidade_comprar > 0:
                    # Verificar se é momento de comprar (baseado na frequência)
                    if self._verificar_momento_compra(data_referencia, politica.categoria.nome, perfil):
                        # Determinar valor por cabeça
                        valor_por_cabeca = None
                        valor_total = None
                        
                        if politica.usar_valor_personalizado and politica.valor_por_cabeca_personalizado:
                            valor_por_cabeca = politica.valor_por_cabeca_personalizado
                            valor_total = politica.quantidade_comprar * valor_por_cabeca
                        else:
                            # Usar valor do inventário ou CEPEA do ano da projeção
                            ano_mov = data_referencia.year if data_referencia else None
                            inventario_item = InventarioRebanho.objects.filter(
                                propriedade=propriedade,
                                categoria=politica.categoria
                            ).first()
                            if inventario_item and inventario_item.valor_por_cabeca:
                                valor_por_cabeca = inventario_item.valor_por_cabeca
                            else:
                                # Usar preço CEPEA do ano da projeção
                                from gestao_rural.views import obter_valor_padrao_por_categoria
                                valor_por_cabeca = obter_valor_padrao_por_categoria(
                                    politica.categoria, propriedade, ano_mov
                                )
                            valor_total = politica.quantidade_comprar * valor_por_cabeca
                        
                        compras.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='COMPRA',
                            categoria=politica.categoria,
                            quantidade=politica.quantidade_comprar,
                            valor_por_cabeca=valor_por_cabeca,
                            valor_total=valor_total,
                            observacao=f'Compra configurada - {politica.categoria.nome} ({politica.quantidade_comprar} cabeças)'
                        ))
                        
                        print(f"    [COMPRA] Compra configurada: {politica.quantidade_comprar} {politica.categoria.nome}")
        else:
            # Fallback para estratégias automáticas baseadas no perfil
            print(f"    [COMPRA] Usando estrategias automaticas (perfil: {perfil.value})")
            estrategias_compras = estrategias.get('compras', {})
        
        # Processar estratégias automáticas apenas se não houver políticas configuradas
        if not politicas_vendas.exists():
            for categoria, quantidade_compra in estrategias_compras.items():
                # Verificar se é momento de comprar
                if self._verificar_momento_compra(data_referencia, categoria, perfil):
                    try:
                        categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                        
                        compras.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='COMPRA',
                            categoria=categoria_obj,
                            quantidade=quantidade_compra,
                            observacao=f'Compra automática - {categoria} ({quantidade_compra} cabeças) - Perfil: {perfil.value}'
                        ))
                        
                        print(f"    [COMPRA] Compra automatica: {quantidade_compra} {categoria}")
                        
                    except CategoriaAnimal.DoesNotExist:
                        print(f"    [AVISO] Categoria nao encontrada: {categoria}")
        
        return compras
    
    def _gerar_transferencias_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais_ano: Dict[str, int], perfil: PerfilFazenda, ano_atual: int) -> List[MovimentacaoProjetada]:
        """
        Gera transferências automáticas entre fazendas do mesmo produtor.
        Vacas de descarte e garrotes são transferências, não vendas.
        IMPORTANTE: Apenas transfere o estoque inicial do ano (não animais criados durante o ano).
        Executado apenas em janeiro de cada ano.
        
        ========================================================================
        REGRA PERMANENTE - CONFIGURAÇÃO PADRÃO CANTA GALO:
        NÃO TRANSFERIR SE SALDO FOR NEGATIVO OU ZERO
        ========================================================================
        Esta regra garante que transferências só ocorram quando há saldo
        disponível suficiente, evitando saldos negativos na projeção.
        O saldo passado como parâmetro já considera promoções criadas.
        ========================================================================
        """
        from .models import CategoriaAnimal, ConfiguracaoVenda
        
        transferencias = []
        
        # Identificar categorias que devem ser transferências
        categorias_transferencia = []
        for categoria_nome in saldos_iniciais_ano.keys():
            categoria_lower = categoria_nome.lower()
            # Vacas de descarte e garrotes devem ser transferências
            if 'descarte' in categoria_lower or 'garrote' in categoria_lower:
                categorias_transferencia.append(categoria_nome)
        
        if not categorias_transferencia:
            return transferencias
        
        print(f"    [TRANSFERENCIA] Processando transferencias do estoque inicial do ano {ano_atual} para: {categorias_transferencia}")
        
        # Buscar configurações de transferência
        configuracoes = ConfiguracaoVenda.objects.filter(
            propriedade=propriedade,
            tipo_reposicao='TRANSFERENCIA',
            ativo=True
        )
        
        for categoria_nome in categorias_transferencia:
            # ====================================================================
            # REGRA PERMANENTE - CONFIGURAÇÃO PADRÃO CANTA GALO:
            # NÃO TRANSFERIR SE SALDO FOR NEGATIVO OU ZERO
            # ====================================================================
            # CRÍTICO: saldos_iniciais_ano agora já vem com saldo após promoções
            # Esta regra é PERMANENTE e não deve ser alterada
            quantidade_disponivel = saldos_iniciais_ano.get(categoria_nome, 0)
            
            if quantidade_disponivel <= 0:
                print(f"    [AVISO] Sem saldo disponivel de {categoria_nome} para transferencia (saldo: {quantidade_disponivel}) - REGRA PERMANENTE")
                continue
            
            print(f"    [ESTOQUE] Estoque inicial de {categoria_nome}: {quantidade_disponivel} cabeças")
            
            try:
                categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                
                # Buscar configuração específica para esta categoria
                config = configuracoes.filter(categoria_venda=categoria_obj).first()
                
                if config and config.fazenda_destino:
                    # Usar configuração do usuário
                    # Transferir 100% do estoque inicial por padrão
                    quantidade_transferencia = quantidade_disponivel
                    
                    if config.quantidade_transferencia > 0:
                        # Se houver quantidade configurada, usar o mínimo entre configurado e disponível
                        quantidade_transferencia = min(quantidade_transferencia, config.quantidade_transferencia)
                    
                    # Transferência de saída (da fazenda atual) - apenas estoque inicial
                    transferencias.append(MovimentacaoProjetada(
                        propriedade=propriedade,
                        data_movimentacao=data_referencia,
                        tipo_movimentacao='TRANSFERENCIA_SAIDA',
                        categoria=categoria_obj,
                        quantidade=quantidade_transferencia,
                        observacao=f'Transferência automática do estoque inicial do ano {ano_atual} - {categoria_nome} → {config.fazenda_destino.nome_propriedade}'
                    ))
                    
                    # Transferência de entrada (na fazenda destino) - IMPORTANTE: criar também a entrada
                    transferencias.append(MovimentacaoProjetada(
                        propriedade=config.fazenda_destino,
                        data_movimentacao=data_referencia,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                        categoria=categoria_obj,
                        quantidade=quantidade_transferencia,
                        observacao=f'Transferência automática do estoque inicial do ano {ano_atual} - {categoria_nome} de {propriedade.nome_propriedade}'
                    ))
                    
                    print(f"    [TRANSFERENCIA] Transferencia configurada (estoque inicial): {quantidade_transferencia}/{quantidade_disponivel} {categoria_nome} -> {config.fazenda_destino.nome_propriedade}")
                else:
                    # Transferência padrão (100% do estoque inicial)
                    # Nota: Sem fazenda destino configurada, apenas registra a saída
                    transferencias.append(MovimentacaoProjetada(
                        propriedade=propriedade,
                        data_movimentacao=data_referencia,
                        tipo_movimentacao='TRANSFERENCIA_SAIDA',
                        categoria=categoria_obj,
                        quantidade=quantidade_disponivel,
                        observacao=f'Transferência automática do estoque inicial do ano {ano_atual} - {categoria_nome} (100% do estoque inicial)'
                    ))
                    
                    print(f"    [TRANSFERENCIA] Transferencia automatica (estoque inicial): {quantidade_disponivel} {categoria_nome}")
                    
            except CategoriaAnimal.DoesNotExist:
                print(f"    [AVISO] Categoria '{categoria_nome}' nao encontrada para transferencia")
        
        return transferencias
    
    def _verificar_momento_venda(self, data_referencia: datetime, categoria: str, perfil: PerfilFazenda) -> bool:
        """Verifica se é o momento correto para vender baseado no perfil"""
        mes = data_referencia.month
        
        if perfil == PerfilFazenda.SO_CRIA:
            # Fazenda de cria vende bezerros a cada 2 meses
            if 'Bezerro' in categoria or 'Bezerra' in categoria:
                return mes % 2 == 0
        elif perfil == PerfilFazenda.SO_RECRIA:
            # Fazenda de recria vende animais prontos a cada 3 meses
            return mes % 3 == 0
        elif perfil == PerfilFazenda.SO_ENGORDA:
            # Fazenda de engorda vende animais prontos a cada 2 meses
            return mes % 2 == 0
        elif perfil == PerfilFazenda.CICLO_COMPLETO:
            # Ciclo completo vende conforme disponibilidade
            return mes % 2 == 0
        
        return False
    
    def _verificar_momento_compra(self, data_referencia: datetime, categoria: str, perfil: PerfilFazenda) -> bool:
        """Verifica se é o momento correto para comprar baseado no perfil"""
        mes = data_referencia.month
        
        if perfil == PerfilFazenda.SO_RECRIA:
            # Recria compra bezerros a cada 2 meses
            return mes % 2 == 0
        elif perfil == PerfilFazenda.SO_ENGORDA:
            # Engorda compra garrotes mensalmente
            return True
        elif perfil == PerfilFazenda.SO_CRIA:
            # Cria compra novilhas anualmente
            return mes == 12
        
        return False
    
    def _atualizar_saldos_pos_movimentacoes(self, saldos_iniciais: Dict[str, int], nascimentos: List, promocoes: List, mortes: List, vendas: List, compras: List, transferencias: List) -> Dict[str, int]:
        """Atualiza saldos após as movimentações do mês"""
        saldos_atualizados = saldos_iniciais.copy()
        
        # Aplicar todas as movimentações
        for movimentacoes in [nascimentos, promocoes, mortes, vendas, compras, transferencias]:
            for mov in movimentacoes:
                categoria = mov.categoria.nome
                
                if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
                    saldos_atualizados[categoria] = saldos_atualizados.get(categoria, 0) + mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
                    saldos_atualizados[categoria] = saldos_atualizados.get(categoria, 0) - mov.quantidade
        
        # Garantir que não há saldos negativos
        for categoria in saldos_atualizados:
            if saldos_atualizados[categoria] < 0:
                saldos_atualizados[categoria] = 0
        
        return saldos_atualizados
    
    def calcular_valores_totais_por_categoria(self, inventario_inicial: List[InventarioRebanho], movimentacoes: List[MovimentacaoProjetada]) -> Dict[str, Dict[str, Any]]:
        """Calcula valores totais por categoria considerando todas as movimentações"""
        valores_categorias = {}
        
        # Inicializar com valores do inventário
        for item in inventario_inicial:
            valores_categorias[item.categoria.nome] = {
                'quantidade_inicial': item.quantidade,
                'valor_unitario': item.valor_por_cabeca or Decimal('0.00'),
                'valor_total_inicial': (item.valor_por_cabeca or Decimal('0.00')) * Decimal(str(item.quantidade)),
                'saldo_atual': item.quantidade,
                'valor_total_atual': (item.valor_por_cabeca or Decimal('0.00')) * Decimal(str(item.quantidade))
            }
        
        # Processar movimentações para atualizar saldos
        for mov in movimentacoes:
            categoria = mov.categoria.nome
            
            if categoria not in valores_categorias:
                # Categoria nova (não estava no inventário inicial)
                valores_categorias[categoria] = {
                    'quantidade_inicial': 0,
                    'valor_unitario': Decimal('2000.00'),  # Valor padrão
                    'valor_total_inicial': Decimal('0.00'),
                    'saldo_atual': 0,
                    'valor_total_atual': Decimal('0.00')
                }
            
            # Atualizar saldo baseado no tipo de movimentação
            if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
                valores_categorias[categoria]['saldo_atual'] += mov.quantidade
            elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
                valores_categorias[categoria]['saldo_atual'] -= mov.quantidade
            
            # Recalcular valor total atual
            valores_categorias[categoria]['valor_total_atual'] = (
                valores_categorias[categoria]['valor_unitario'] * 
                Decimal(str(valores_categorias[categoria]['saldo_atual']))
            )
        
        return valores_categorias

# Instância global do sistema
sistema_movimentacoes = SistemaMovimentacoesAutomaticas()



