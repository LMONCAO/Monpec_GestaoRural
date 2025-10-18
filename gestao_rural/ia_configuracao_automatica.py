# -*- coding: utf-8 -*-
"""
IA para Configuração Automática de Projeção Pecuária
Analisa o inventário e preenche automaticamente parâmetros para rentabilidade e crescimento
"""

from decimal import Decimal
from typing import Dict, List, Any, Tuple
from .ia_perfis_fazendas import PERFIS_FAZENDAS, TipoFazenda, detectar_perfil_fazenda

class IAConfiguracaoAutomatica:
    """IA que configura automaticamente parâmetros para rentabilidade e crescimento"""
    
    def __init__(self):
        self.perfis = PERFIS_FAZENDAS
    
    def analisar_inventario_e_configurar(self, inventario_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o inventário e retorna configuração automática otimizada
        """
        # Converter dados do inventário para formato esperado
        inventario = {}
        for item in inventario_data:
            categoria = item.get('categoria', {}).get('nome', '')
            quantidade = item.get('quantidade', 0)
            if categoria and quantidade > 0:
                inventario[categoria] = quantidade
        
        # Detectar perfil da fazenda
        perfil_tipo = detectar_perfil_fazenda(inventario, {})
        perfil = self.perfis[perfil_tipo]
        
        # Calcular configuração otimizada
        configuracao = self._calcular_configuracao_otimizada(inventario, perfil)
        
        return {
            'perfil_detectado': perfil_tipo.value,
            'nome_perfil': perfil.nome,
            'descricao': perfil.descricao,
            'inventario_analisado': inventario,
            'total_animais': sum(inventario.values()),
            'configuracao_otimizada': configuracao,
            'estrategia_vendas': perfil.estrategia_vendas,
            'estrategia_compras': perfil.estrategia_compras,
            'projecao_rentabilidade': self._calcular_projecao_rentabilidade(inventario, perfil),
            'metas_crescimento': perfil.metas_crescimento
        }
    
    def _calcular_configuracao_otimizada(self, inventario: Dict[str, int], perfil) -> Dict[str, Any]:
        """
        Calcula configuração otimizada para rentabilidade e crescimento
        """
        total_animais = sum(inventario.values())
        
        # Configuração baseada no perfil
        configuracao = {
            # Parâmetros de produção
            'natalidade': perfil.parametros_producao['natalidade'],
            'mortalidade_bezerros': perfil.parametros_producao['mortalidade_bezerros'],
            'mortalidade_adultos': perfil.parametros_producao['mortalidade_adultos'],
            'periodicidade': 'MENSAL',
            'anos_projecao': 5,
            
            # Estratégias otimizadas
            'estrategia_vendas': perfil.estrategia_vendas,
            'estrategia_compras': perfil.estrategia_compras,
            
            # Configurações de vendas automáticas
            'vendas_automaticas': self._gerar_vendas_automaticas(inventario, perfil),
            
            # Configurações de compras automáticas
            'compras_automaticas': self._gerar_compras_automaticas(inventario, perfil),
            
            # Objetivos financeiros
            'objetivo_receita_anual': total_animais * perfil.indicadores_financeiros['receita_por_animal_ano'],
            'objetivo_custo_anual': total_animais * perfil.indicadores_financeiros['custo_por_animal_ano'],
            'objetivo_lucro_anual': total_animais * (perfil.indicadores_financeiros['receita_por_animal_ano'] - perfil.indicadores_financeiros['custo_por_animal_ano']),
            'margem_lucro_objetivo': perfil.metas_crescimento['margem_lucro_minima'] * 100,
            
            # Crescimento do rebanho
            'crescimento_rebanho_objetivo': perfil.metas_crescimento['crescimento_rebanho_anual'] * 100,
            'crescimento_receita_objetivo': perfil.metas_crescimento['crescimento_receita_anual'] * 100
        }
        
        return configuracao
    
    def _gerar_vendas_automaticas(self, inventario: Dict[str, int], perfil) -> List[Dict[str, Any]]:
        """
        Gera configurações automáticas de vendas baseadas no perfil
        """
        vendas = []
        
        for categoria, quantidade in inventario.items():
            if quantidade > 0:
                # Obter percentual de venda baseado no perfil
                percentual_venda = perfil.estrategia_vendas.get(categoria, 0.0)
                
                if percentual_venda > 0:
                    # Calcular quantidade para venda
                    quantidade_venda = int(quantidade * percentual_venda)
                    
                    if quantidade_venda > 0:
                        # Definir frequência baseada no perfil
                        if perfil.tipo == TipoFazenda.SO_CRIA:
                            frequencia = 'BIMESTRAL'  # Vende bezerros a cada 2 meses
                        elif perfil.tipo == TipoFazenda.SO_ENGORDA:
                            frequencia = 'MENSAL'     # Vende animais prontos mensalmente
                        elif perfil.tipo == TipoFazenda.CONFINAMENTO:
                            frequencia = 'TRIMESTRAL' # Vende lotes de confinamento
                        else:
                            frequencia = 'BIMESTRAL'  # Padrão
                        
                        # Calcular valor unitário baseado no perfil
                        valor_unitario = self._calcular_valor_unitario_venda(categoria, perfil)
                        
                        vendas.append({
                            'categoria': categoria,
                            'quantidade': quantidade_venda,
                            'frequencia': frequencia,
                            'valor_unitario': valor_unitario,
                            'percentual': percentual_venda * 100,
                            'justificativa': f"Venda estratégica para {perfil.nome.lower()}"
                        })
        
        return vendas
    
    def _gerar_compras_automaticas(self, inventario: Dict[str, int], perfil) -> List[Dict[str, Any]]:
        """
        Gera configurações automáticas de compras baseadas no perfil
        """
        compras = []
        
        # Analisar necessidades de compra baseadas no perfil
        if perfil.tipo in [TipoFazenda.SO_RECRIA, TipoFazenda.SO_ENGORDA, TipoFazenda.CONFINAMENTO]:
            # Fazendas que compram animais
            categorias_compra = ['Bezerros (0-12m)', 'Bezerras (0-12m)', 'Garrotes (12-24m)', 'Novilhas (12-24m)']
            
            for categoria in categorias_compra:
                # Calcular necessidade baseada no perfil
                if perfil.tipo == TipoFazenda.SO_RECRIA:
                    if 'Bezerro' in categoria:
                        quantidade_compra = 50  # Compra bezerros para recria
                        frequencia = 'BIMESTRAL'
                    else:
                        continue
                elif perfil.tipo == TipoFazenda.SO_ENGORDA:
                    if 'Garrotes' in categoria or 'Novilhas' in categoria:
                        quantidade_compra = 30  # Compra animais para engorda
                        frequencia = 'MENSAL'
                    else:
                        continue
                elif perfil.tipo == TipoFazenda.CONFINAMENTO:
                    if 'Garrotes' in categoria:
                        quantidade_compra = 100  # Compra lotes para confinamento
                        frequencia = 'TRIMESTRAL'
                    else:
                        continue
                else:
                    continue
                
                # Calcular valor unitário baseado no perfil
                valor_unitario = self._calcular_valor_unitario_compra(categoria, perfil)
                
                compras.append({
                    'categoria': categoria,
                    'quantidade': quantidade_compra,
                    'frequencia': frequencia,
                    'valor_unitario': valor_unitario,
                    'justificativa': f"Compra estratégica para {perfil.nome.lower()}"
                })
        
        # Para fazendas de ciclo completo, comprar fêmeas para reposição
        elif perfil.tipo == TipoFazenda.CICLO_COMPLETO:
            # Calcular necessidade de reposição
            total_femeas = sum(quantidade for categoria, quantidade in inventario.items() 
                             if any(femea in categoria for femea in ['Multíparas', 'Primíparas', 'Novilhas', 'Bezerras']))
            
            if total_femeas > 0:
                # Comprar 20% de fêmeas para reposição anual
                quantidade_reposicao = max(10, int(total_femeas * 0.20))
                
                compras.append({
                    'categoria': 'Novilhas (12-24m)',
                    'quantidade': quantidade_reposicao,
                    'frequencia': 'ANUAL',
                    'valor_unitario': 5000.00,
                    'justificativa': 'Reposição de matrizes para ciclo completo'
                })
        
        return compras
    
    def _calcular_valor_unitario_venda(self, categoria: str, perfil) -> float:
        """
        Calcula valor unitário de venda baseado na categoria e perfil
        """
        # Valores base por categoria (R$)
        valores_base = {
            'Bezerros (0-12m)': 2000.00,
            'Bezerras (0-12m)': 1800.00,
            'Garrotes (12-24m)': 3500.00,
            'Novilhas (12-24m)': 4000.00,
            'Bois (24-36m)': 4500.00,
            'Bois Magros (24-36m)': 4000.00,
            'Multíparas (>36m)': 3500.00,
            'Primíparas (24-36m)': 4500.00,
            'Vacas de Descarte': 3000.00,
            'Touros': 6000.00
        }
        
        valor_base = valores_base.get(categoria, 2000.00)
        
        # Ajustar baseado no perfil
        if perfil.tipo == TipoFazenda.SO_CRIA:
            # Fazendas de cria vendem bezerros com valor premium
            if 'Bezerro' in categoria:
                valor_base *= 1.1
        elif perfil.tipo == TipoFazenda.SO_ENGORDA:
            # Fazendas de engorda vendem animais prontos com valor premium
            if 'Boi' in categoria:
                valor_base *= 1.15
        elif perfil.tipo == TipoFazenda.CONFINAMENTO:
            # Confinamento vende animais com peso e qualidade premium
            valor_base *= 1.2
        
        return valor_base
    
    def _calcular_valor_unitario_compra(self, categoria: str, perfil) -> float:
        """
        Calcula valor unitário de compra baseado na categoria e perfil
        """
        # Valores base por categoria (R$)
        valores_base = {
            'Bezerros (0-12m)': 1800.00,
            'Bezerras (0-12m)': 1600.00,
            'Garrotes (12-24m)': 3200.00,
            'Novilhas (12-24m)': 3800.00,
            'Bois (24-36m)': 4200.00,
            'Bois Magros (24-36m)': 3800.00,
            'Multíparas (>36m)': 3200.00,
            'Primíparas (24-36m)': 4200.00,
            'Vacas de Descarte': 2800.00,
            'Touros': 5500.00
        }
        
        valor_base = valores_base.get(categoria, 2000.00)
        
        # Ajustar baseado no perfil
        if perfil.tipo == TipoFazenda.SO_RECRIA:
            # Fazendas de recria compram bezerros com desconto por volume
            if 'Bezerro' in categoria:
                valor_base *= 0.95
        elif perfil.tipo == TipoFazenda.SO_ENGORDA:
            # Fazendas de engorda pagam valor justo por animais prontos
            valor_base *= 1.0
        elif perfil.tipo == TipoFazenda.CONFINAMENTO:
            # Confinamento compra em volume, pode ter desconto
            valor_base *= 0.98
        
        return valor_base
    
    def _calcular_projecao_rentabilidade(self, inventario: Dict[str, int], perfil) -> Dict[str, Any]:
        """
        Calcula projeção de rentabilidade para 5 anos
        """
        total_animais = sum(inventario.values())
        
        # Valores base por animal
        receita_por_animal = perfil.indicadores_financeiros['receita_por_animal_ano']
        custo_por_animal = perfil.indicadores_financeiros['custo_por_animal_ano']
        crescimento_rebanho = perfil.metas_crescimento['crescimento_rebanho_anual']
        
        projecao = {
            'anos': [],
            'total_receita': 0,
            'total_custo': 0,
            'total_lucro': 0,
            'crescimento_final': 0
        }
        
        rebanho_atual = total_animais
        receita_acumulada = 0
        custo_acumulado = 0
        
        for ano in range(1, 6):
            # Crescimento do rebanho
            crescimento_anual = rebanho_atual * crescimento_rebanho
            rebanho_atual += crescimento_anual
            
            # Receitas e custos com inflação (5% ao ano)
            fator_inflacao = 1.05 ** ano
            receita_ano = rebanho_atual * receita_por_animal * fator_inflacao
            custo_ano = rebanho_atual * custo_por_animal * fator_inflacao
            lucro_ano = receita_ano - custo_ano
            
            receita_acumulada += receita_ano
            custo_acumulado += custo_ano
            
            projecao['anos'].append({
                'ano': ano,
                'rebanho': int(rebanho_atual),
                'receita': receita_ano,
                'custo': custo_ano,
                'lucro': lucro_ano,
                'margem': (lucro_ano / receita_ano) * 100 if receita_ano > 0 else 0
            })
        
        projecao['total_receita'] = receita_acumulada
        projecao['total_custo'] = custo_acumulada
        projecao['total_lucro'] = receita_acumulada - custo_acumulada
        projecao['crescimento_final'] = ((rebanho_atual - total_animais) / total_animais) * 100
        
        return projecao
    
    def gerar_relatorio_configuracao(self, resultado_analise: Dict[str, Any]) -> str:
        """
        Gera relatório HTML da configuração automática
        """
        perfil = resultado_analise['perfil_detectado']
        config = resultado_analise['configuracao_otimizada']
        projecao = resultado_analise['projecao_rentabilidade']
        
        html = f"""
        <div class="card">
            <div class="card-header bg-success text-white">
                <h4><i class="fas fa-robot"></i> Configuração Automática - {perfil}</h4>
                <p class="mb-0">IA configurou automaticamente para rentabilidade e crescimento</p>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-cogs"></i> Parâmetros Configurados</h5>
                        <ul class="list-unstyled">
                            <li><strong>Natalidade:</strong> {config['natalidade']*100:.1f}%</li>
                            <li><strong>Mortalidade Bezerros:</strong> {config['mortalidade_bezerros']*100:.1f}%</li>
                            <li><strong>Mortalidade Adultos:</strong> {config['mortalidade_adultos']*100:.1f}%</li>
                            <li><strong>Periodicidade:</strong> {config['periodicidade']}</li>
                            <li><strong>Anos de Projeção:</strong> {config['anos_projecao']}</li>
                        </ul>
                        
                        <h5><i class="fas fa-chart-line"></i> Objetivos Financeiros</h5>
                        <ul class="list-unstyled">
                            <li><strong>Receita Anual:</strong> R$ {config['objetivo_receita_anual']:,.2f}</li>
                            <li><strong>Custo Anual:</strong> R$ {config['objetivo_custo_anual']:,.2f}</li>
                            <li><strong>Lucro Anual:</strong> R$ {config['objetivo_lucro_anual']:,.2f}</li>
                            <li><strong>Margem de Lucro:</strong> {config['margem_lucro_objetivo']:.1f}%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-seedling"></i> Crescimento do Rebanho</h5>
                        <ul class="list-unstyled">
                            <li><strong>Crescimento Anual:</strong> {config['crescimento_rebanho_objetivo']:.1f}%</li>
                            <li><strong>Crescimento Receita:</strong> {config['crescimento_receita_objetivo']:.1f}%</li>
                            <li><strong>Total de Animais:</strong> {resultado_analise['total_animais']}</li>
                        </ul>
                        
                        <h5><i class="fas fa-calendar"></i> Projeção 5 Anos</h5>
                        <ul class="list-unstyled">
                            <li><strong>Receita Total:</strong> R$ {projecao['total_receita']:,.2f}</li>
                            <li><strong>Custo Total:</strong> R$ {projecao['total_custo']:,.2f}</li>
                            <li><strong>Lucro Total:</strong> R$ {projecao['total_lucro']:,.2f}</li>
                            <li><strong>Crescimento Final:</strong> {projecao['crescimento_final']:.1f}%</li>
                        </ul>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h5><i class="fas fa-shopping-cart"></i> Vendas Configuradas</h5>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Categoria</th>
                                        <th>Quantidade</th>
                                        <th>Frequência</th>
                                        <th>Valor Unitário</th>
                                        <th>Justificativa</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        for venda in config['vendas_automaticas']:
            html += f"""
                                    <tr>
                                        <td>{venda['categoria']}</td>
                                        <td>{venda['quantidade']}</td>
                                        <td>{venda['frequencia']}</td>
                                        <td>R$ {venda['valor_unitario']:,.2f}</td>
                                        <td>{venda['justificativa']}</td>
                                    </tr>
            """
        
        html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h5><i class="fas fa-shopping-bag"></i> Compras Configuradas</h5>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Categoria</th>
                                        <th>Quantidade</th>
                                        <th>Frequência</th>
                                        <th>Valor Unitário</th>
                                        <th>Justificativa</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        for compra in config['compras_automaticas']:
            html += f"""
                                    <tr>
                                        <td>{compra['categoria']}</td>
                                        <td>{compra['quantidade']}</td>
                                        <td>{compra['frequencia']}</td>
                                        <td>R$ {compra['valor_unitario']:,.2f}</td>
                                        <td>{compra['justificativa']}</td>
                                    </tr>
            """
        
        html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-success mt-3">
                    <h6><i class="fas fa-check-circle"></i> Configuração Aplicada com Sucesso!</h6>
                    <p class="mb-0">A IA configurou automaticamente todos os parâmetros para garantir rentabilidade e crescimento do rebanho baseado no seu inventário inicial.</p>
                </div>
            </div>
        </div>
        """
        
        return html

# Instância global da IA
ia_configuracao = IAConfiguracaoAutomatica()



