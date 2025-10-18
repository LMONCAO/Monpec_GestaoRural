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
        
    def gerar_movimentacoes_completas(self, propriedade, parametros, inventario_inicial, anos_projecao: int) -> List[MovimentacaoProjetada]:
        """
        Gera todas as movimentações automaticamente baseadas no perfil da fazenda
        """
        # Identificar perfil da fazenda
        identificacao = self.identificador.identificar_perfil_fazenda(inventario_inicial, parametros)
        perfil = identificacao['perfil_detectado']
        
        print(f"🏭 Perfil detectado: {perfil.value}")
        print(f"📊 Estratégias: {identificacao['estrategias']}")
        
        # Limpar movimentações existentes
        MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
        
        movimentacoes = []
        
        # Gerar movimentações para cada ano
        for ano in range(anos_projecao):
            ano_atual = datetime.now().year + ano
            print(f"\n📅 Processando ano {ano_atual}...")
            
            # Calcular saldos iniciais para o ano
            saldos_iniciais = self._calcular_saldos_iniciais_ano(ano, inventario_inicial, movimentacoes)
            
            # Gerar movimentações mensais
            for mes in range(1, 13):
                data_referencia = datetime(ano_atual, mes, 15)
                print(f"  📆 Mês {mes:02d}/{ano_atual}")
                
                # 1. NASCIMENTOS (baseado em matrizes existentes)
                nascimentos = self._gerar_nascimentos(propriedade, data_referencia, saldos_iniciais, parametros, perfil)
                movimentacoes.extend(nascimentos)
                
                # 2. EVOLUÇÃO DE IDADE (promoção de categorias)
                promocoes = self._gerar_evolucao_idade(propriedade, data_referencia, saldos_iniciais, perfil)
                movimentacoes.extend(promocoes)
                
                # 3. MORTES (baseado em mortalidade)
                mortes = self._gerar_mortes(propriedade, data_referencia, saldos_iniciais, parametros)
                movimentacoes.extend(mortes)
                
                # 4. VENDAS (baseado no perfil)
                vendas = self._gerar_vendas_automaticas(propriedade, data_referencia, saldos_iniciais, perfil, identificacao['estrategias'])
                movimentacoes.extend(vendas)
                
                # 5. COMPRAS (baseado no perfil)
                compras = self._gerar_compras_automaticas(propriedade, data_referencia, saldos_iniciais, perfil, identificacao['estrategias'])
                movimentacoes.extend(compras)
                
                # 6. TRANSFERÊNCIAS (entre fazendas do mesmo produtor)
                transferencias = self._gerar_transferencias_automaticas(propriedade, data_referencia, saldos_iniciais, perfil)
                movimentacoes.extend(transferencias)
                
                # Atualizar saldos após as movimentações do mês
                saldos_iniciais = self._atualizar_saldos_pos_movimentacoes(saldos_iniciais, nascimentos, promocoes, mortes, vendas, compras, transferencias)
        
        # Salvar todas as movimentações no banco
        for movimentacao in movimentacoes:
            movimentacao.save()
        
        print(f"\n✅ Total de movimentações geradas: {len(movimentacoes)}")
        return movimentacoes
    
    def _calcular_saldos_iniciais_ano(self, ano: int, inventario_inicial: List[InventarioRebanho], movimentacoes_anteriores: List[MovimentacaoProjetada]) -> Dict[str, int]:
        """Calcula saldos iniciais para o ano baseado no inventário e movimentações anteriores"""
        if ano == 0:
            # Primeiro ano: usar inventário inicial
            saldos = {}
            for item in inventario_inicial:
                saldos[item.categoria.nome] = item.quantidade
            return saldos
        else:
            # Anos seguintes: calcular baseado nas movimentações do ano anterior
            return self._calcular_saldos_finais_ano_anterior(movimentacoes_anteriores, ano)
    
    def _calcular_saldos_finais_ano_anterior(self, movimentacoes: List[MovimentacaoProjetada], ano_atual: int) -> Dict[str, int]:
        """Calcula saldos finais do ano anterior"""
        ano_anterior = datetime.now().year + ano_atual - 1
        
        # Agrupar movimentações por categoria
        saldos = defaultdict(int)
        
        for mov in movimentacoes:
            if mov.data_movimentacao.year == ano_anterior:
                categoria = mov.categoria.nome
                
                if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA']:
                    saldos[categoria] += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA']:
                    saldos[categoria] -= mov.quantidade
                elif mov.tipo_movimentacao == 'PROMOCAO_ENTRADA':
                    saldos[categoria] += mov.quantidade
                elif mov.tipo_movimentacao == 'PROMOCAO_SAIDA':
                    saldos[categoria] -= mov.quantidade
        
        return dict(saldos)
    
    def _gerar_nascimentos(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], parametros, perfil: PerfilFazenda) -> List[MovimentacaoProjetada]:
        """Gera nascimentos baseado nas matrizes existentes"""
        nascimentos = []
        
        # Buscar matrizes (Multíparas e Primíparas)
        matrizes = saldos_iniciais.get('Multíparas (>36m)', 0) + saldos_iniciais.get('Primíparas (24-36m)', 0)
        
        if matrizes > 0:
            # Calcular nascimentos baseado na natalidade
            taxa_natalidade_mensal = parametros.taxa_natalidade_anual / 100 / 12
            total_nascimentos = int(matrizes * taxa_natalidade_mensal)
            
            if total_nascimentos > 0:
                # Distribuir nascimentos entre bezerros e bezerras (50/50)
                bezerros = total_nascimentos // 2
                bezerras = total_nascimentos - bezerros
                
                try:
                    categoria_bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
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
                    
                    print(f"    👶 Nascimentos: {bezerros} bezerros + {bezerras} bezerras = {total_nascimentos}")
                    
                except CategoriaAnimal.DoesNotExist:
                    print("    ⚠️ Categorias de bezerros não encontradas")
        
        return nascimentos
    
    def _gerar_evolucao_idade(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda) -> List[MovimentacaoProjetada]:
        """Gera evolução automática de idade dos animais"""
        promocoes = []
        
        # Mapeamento de evolução de idade
        evolucoes = {
            'Bezerros (0-12m)': 'Garrotes (12-24m)',
            'Bezerras (0-12m)': 'Novilhas (12-24m)',
            'Garrotes (12-24m)': 'Bois (24-36m)',
            'Novilhas (12-24m)': 'Primíparas (24-36m)',
            'Primíparas (24-36m)': 'Multíparas (>36m)'
        }
        
        for categoria_origem, categoria_destino in evolucoes.items():
            quantidade_origem = saldos_iniciais.get(categoria_origem, 0)
            
            if quantidade_origem > 0:
                # Calcular quantos animais evoluem (baseado na idade)
                taxa_evolucao = self._calcular_taxa_evolucao_idade(categoria_origem, data_referencia.month)
                quantidade_evolui = int(quantidade_origem * taxa_evolucao)
                
                if quantidade_evolui > 0:
                    try:
                        categoria_origem_obj = CategoriaAnimal.objects.get(nome=categoria_origem)
                        categoria_destino_obj = CategoriaAnimal.objects.get(nome=categoria_destino)
                        
                        # Saída da categoria origem
                        promocoes.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            categoria=categoria_origem_obj,
                            quantidade=quantidade_evolui,
                            observacao=f'Evolução de idade - {categoria_origem} → {categoria_destino}'
                        ))
                        
                        # Entrada na categoria destino
                        promocoes.append(MovimentacaoProjetada(
                            propriedade=propriedade,
                            data_movimentacao=data_referencia,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            categoria=categoria_destino_obj,
                            quantidade=quantidade_evolui,
                            observacao=f'Evolução de idade - {categoria_origem} → {categoria_destino}'
                        ))
                        
                        print(f"    🔄 Evolução: {quantidade_evolui} {categoria_origem} → {categoria_destino}")
                        
                    except CategoriaAnimal.DoesNotExist:
                        print(f"    ⚠️ Categoria não encontrada: {categoria_origem} ou {categoria_destino}")
        
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
                        
                        print(f"    💀 Mortes: {quantidade_mortes} {categoria}")
                        
                    except CategoriaAnimal.DoesNotExist:
                        print(f"    ⚠️ Categoria não encontrada: {categoria}")
        
        return mortes
    
    def _gerar_vendas_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda, estrategias: Dict[str, Any]) -> List[MovimentacaoProjetada]:
        """Gera vendas automáticas baseadas no perfil da fazenda"""
        vendas = []
        
        estrategias_vendas = estrategias.get('vendas', {})
        
        for categoria, percentual_venda in estrategias_vendas.items():
            quantidade_disponivel = saldos_iniciais.get(categoria, 0)
            
            if quantidade_disponivel > 0:
                # Verificar se é momento de vender (baseado na frequência)
                if self._verificar_momento_venda(data_referencia, categoria, perfil):
                    quantidade_venda = int(quantidade_disponivel * percentual_venda)
                    
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
                            
                            print(f"    💰 Venda: {quantidade_venda} {categoria} ({percentual_venda*100:.0f}%)")
                            
                        except CategoriaAnimal.DoesNotExist:
                            print(f"    ⚠️ Categoria não encontrada: {categoria}")
        
        return vendas
    
    def _gerar_compras_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda, estrategias: Dict[str, Any]) -> List[MovimentacaoProjetada]:
        """Gera compras automáticas baseadas no perfil da fazenda"""
        compras = []
        
        estrategias_compras = estrategias.get('compras', {})
        
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
                    
                    print(f"    🛒 Compra: {quantidade_compra} {categoria}")
                    
                except CategoriaAnimal.DoesNotExist:
                    print(f"    ⚠️ Categoria não encontrada: {categoria}")
        
        return compras
    
    def _gerar_transferencias_automaticas(self, propriedade, data_referencia: datetime, saldos_iniciais: Dict[str, int], perfil: PerfilFazenda) -> List[MovimentacaoProjetada]:
        """Gera transferências automáticas entre fazendas do mesmo produtor"""
        transferencias = []
        
        # Por enquanto, não implementar transferências automáticas
        # Pode ser implementado futuramente para sistemas multi-fazenda
        
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



