# -*- coding: utf-8 -*-
"""
IA Avançada para Perfis de Fazendas Pecuárias Brasileiras
Sistema inteligente que identifica o perfil da propriedade e projeta receitas/despesas/crescimento
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class TipoFazenda(Enum):
    """Tipos de fazendas pecuárias brasileiras"""
    CICLO_COMPLETO = "Ciclo Completo"
    SO_CRIA = "Só Cria"
    SO_RECRIA = "Só Recria"
    SO_ENGORDA = "Só Engorda"
    RECRIA_ENGORDA = "Recria + Engorda"
    CONFINAMENTO = "Confinamento"
    CONFINAMENTO_RECRIA = "Confinamento + Recria"
    CONFINAMENTO_ENGORDA = "Confinamento + Engorda"
    CONFINAMENTO_COMPLETO = "Confinamento Completo"

@dataclass
class PerfilFazenda:
    """Perfil detalhado de uma fazenda pecuária"""
    tipo: TipoFazenda
    nome: str
    descricao: str
    caracteristicas: List[str]
    categorias_principais: List[str]
    estrategia_vendas: Dict[str, float]  # % de vendas por categoria
    estrategia_compras: Dict[str, float]  # % de compras por categoria
    parametros_producao: Dict[str, Any]
    metas_crescimento: Dict[str, float]
    indicadores_financeiros: Dict[str, float]

# Perfis detalhados de fazendas brasileiras
PERFIS_FAZENDAS = {
    TipoFazenda.CICLO_COMPLETO: PerfilFazenda(
        tipo=TipoFazenda.CICLO_COMPLETO,
        nome="Fazenda Ciclo Completo",
        descricao="Fazenda que realiza todo o ciclo pecuário: cria, recria e engorda",
        caracteristicas=[
            "Mantém matrizes para reprodução",
            "Recria bezerros até idade de abate",
            "Engorda animais para mercado",
            "Alta diversificação de receitas",
            "Maior controle sobre qualidade"
        ],
        categorias_principais=[
            "Multíparas", "Primíparas", "Novilhas", 
            "Bezerras", "Bezerros", "Garrotes", "Bois"
        ],
        estrategia_vendas={
            "Bois": 0.85,  # 85% dos bois para abate
            "Garrotes": 0.70,  # 70% dos garrotes
            "Bezerros": 0.40,  # 40% dos bezerros
            "Vacas de Descarte": 0.90  # 90% das vacas de descarte
        },
        estrategia_compras={
            "Novilhas": 0.60,  # 60% para reposição
            "Bezerras": 0.30,  # 30% para crescimento
            "Multíparas": 0.10  # 10% para melhoramento genético
        },
        parametros_producao={
            "natalidade": 0.85,
            "mortalidade_bezerros": 0.05,
            "mortalidade_adultos": 0.02,
            "taxa_descarte_vacas": 0.20,
            "peso_abate_boi": 450,  # kg
            "peso_abate_vaca": 350,  # kg
            "idade_abate_boi": 36,  # meses
            "idade_abate_vaca": 48  # meses
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.15,  # 15% ao ano
            "crescimento_receita_anual": 0.20,  # 20% ao ano
            "margem_lucro_minima": 0.25  # 25% de margem
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 2500,  # R$ por animal/ano
            "custo_por_animal_ano": 1800,  # R$ por animal/ano
            "investimento_inicial_por_animal": 3000  # R$ por animal
        }
    ),

    TipoFazenda.SO_CRIA: PerfilFazenda(
        tipo=TipoFazenda.SO_CRIA,
        nome="Fazenda Só Cria",
        descricao="Fazenda especializada apenas na criação de bezerros",
        caracteristicas=[
            "Foco exclusivo na reprodução",
            "Vende bezerros para outras fazendas",
            "Baixo investimento em infraestrutura",
            "Receita rápida e constante",
            "Menor risco operacional"
        ],
        categorias_principais=[
            "Multíparas", "Primíparas", "Novilhas", "Bezerras", "Bezerros"
        ],
        estrategia_vendas={
            "Bezerros": 0.90,  # 90% dos bezerros
            "Bezerras": 0.70,  # 70% das bezerras
            "Vacas de Descarte": 0.95  # 95% das vacas de descarte
        },
        estrategia_compras={
            "Novilhas": 0.80,  # 80% para reposição
            "Multíparas": 0.20  # 20% para melhoramento
        },
        parametros_producao={
            "natalidade": 0.90,
            "mortalidade_bezerros": 0.03,
            "mortalidade_adultos": 0.01,
            "taxa_descarte_vacas": 0.15,
            "idade_venda_bezerro": 8,  # meses
            "peso_venda_bezerro": 200  # kg
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.25,  # 25% ao ano
            "crescimento_receita_anual": 0.30,  # 30% ao ano
            "margem_lucro_minima": 0.35  # 35% de margem
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 1800,
            "custo_por_animal_ano": 1200,
            "investimento_inicial_por_animal": 2000
        }
    ),

    TipoFazenda.SO_RECRIA: PerfilFazenda(
        tipo=TipoFazenda.SO_RECRIA,
        nome="Fazenda Só Recria",
        descricao="Fazenda que compra bezerros e os recria até idade de engorda",
        caracteristicas=[
            "Compra bezerros de fazendas de cria",
            "Recria animais até 18-24 meses",
            "Vende para fazendas de engorda",
            "Foco em ganho de peso eficiente",
            "Rotação rápida de animais"
        ],
        categorias_principais=[
            "Bezerros", "Bezerras", "Garrotes", "Novilhas"
        ],
        estrategia_vendas={
            "Garrotes": 0.95,  # 95% dos garrotes
            "Novilhas": 0.90,  # 90% das novilhas
            "Bezerros": 0.80  # 80% dos bezerros
        },
        estrategia_compras={
            "Bezerros": 0.70,  # 70% de bezerros
            "Bezerras": 0.30  # 30% de bezerras
        },
        parametros_producao={
            "natalidade": 0.00,  # Não reproduz
            "mortalidade_bezerros": 0.02,
            "mortalidade_adultos": 0.01,
            "ganho_peso_diario": 0.8,  # kg/dia
            "idade_venda_recria": 18,  # meses
            "peso_venda_recria": 350  # kg
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.20,
            "crescimento_receita_anual": 0.25,
            "margem_lucro_minima": 0.30
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 2200,
            "custo_por_animal_ano": 1600,
            "investimento_inicial_por_animal": 2500
        }
    ),

    TipoFazenda.SO_ENGORDA: PerfilFazenda(
        tipo=TipoFazenda.SO_ENGORDA,
        nome="Fazenda Só Engorda",
        descricao="Fazenda que compra animais para engorda e abate",
        caracteristicas=[
            "Compra animais de 18-24 meses",
            "Engorda até peso de abate",
            "Foco em eficiência alimentar",
            "Rotação rápida de capital",
            "Alta produtividade por hectare"
        ],
        categorias_principais=[
            "Garrotes", "Novilhas", "Bois", "Bois Magros"
        ],
        estrategia_vendas={
            "Bois": 0.98,  # 98% dos bois
            "Bois Magros": 0.95,  # 95% dos bois magros
            "Garrotes": 0.90  # 90% dos garrotes
        },
        estrategia_compras={
            "Garrotes": 0.60,  # 60% de garrotes
            "Novilhas": 0.40  # 40% de novilhas
        },
        parametros_producao={
            "natalidade": 0.00,
            "mortalidade_bezerros": 0.00,
            "mortalidade_adultos": 0.01,
            "ganho_peso_diario": 1.2,  # kg/dia
            "idade_abate": 30,  # meses
            "peso_abate": 450  # kg
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.15,
            "crescimento_receita_anual": 0.20,
            "margem_lucro_minima": 0.25
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 3000,
            "custo_por_animal_ano": 2200,
            "investimento_inicial_por_animal": 3500
        }
    ),

    TipoFazenda.RECRIA_ENGORDA: PerfilFazenda(
        tipo=TipoFazenda.RECRIA_ENGORDA,
        nome="Fazenda Recria + Engorda",
        descricao="Fazenda que recria e engorda animais",
        caracteristicas=[
            "Compra bezerros e os recria",
            "Engorda animais até abate",
            "Maior controle sobre qualidade",
            "Receita diversificada",
            "Eficiência operacional média"
        ],
        categorias_principais=[
            "Bezerros", "Bezerras", "Garrotes", "Novilhas", "Bois"
        ],
        estrategia_vendas={
            "Bois": 0.90,
            "Garrotes": 0.80,
            "Novilhas": 0.70,
            "Bezerros": 0.60
        },
        estrategia_compras={
            "Bezerros": 0.70,
            "Bezerras": 0.30
        },
        parametros_producao={
            "natalidade": 0.00,
            "mortalidade_bezerros": 0.02,
            "mortalidade_adultos": 0.01,
            "ganho_peso_diario": 1.0,
            "idade_abate": 36,
            "peso_abate": 450
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.18,
            "crescimento_receita_anual": 0.23,
            "margem_lucro_minima": 0.28
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 2800,
            "custo_por_animal_ano": 2000,
            "investimento_inicial_por_animal": 3000
        }
    ),

    TipoFazenda.CONFINAMENTO: PerfilFazenda(
        tipo=TipoFazenda.CONFINAMENTO,
        nome="Fazenda Confinamento",
        descricao="Fazenda especializada em confinamento intensivo",
        caracteristicas=[
            "Sistema intensivo de engorda",
            "Alta produtividade por hectare",
            "Controle total da alimentação",
            "Rotação rápida de animais",
            "Alto investimento em infraestrutura"
        ],
        categorias_principais=[
            "Garrotes", "Novilhas", "Bois", "Bois Magros"
        ],
        estrategia_vendas={
            "Bois": 0.99,
            "Bois Magros": 0.98,
            "Garrotes": 0.95
        },
        estrategia_compras={
            "Garrotes": 0.70,
            "Novilhas": 0.30
        },
        parametros_producao={
            "natalidade": 0.00,
            "mortalidade_bezerros": 0.00,
            "mortalidade_adultos": 0.005,
            "ganho_peso_diario": 1.5,
            "idade_abate": 24,
            "peso_abate": 500,
            "periodo_confinamento": 120  # dias
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.12,
            "crescimento_receita_anual": 0.18,
            "margem_lucro_minima": 0.22
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 4000,
            "custo_por_animal_ano": 3000,
            "investimento_inicial_por_animal": 5000
        }
    ),

    TipoFazenda.CONFINAMENTO_RECRIA: PerfilFazenda(
        tipo=TipoFazenda.CONFINAMENTO_RECRIA,
        nome="Fazenda Confinamento + Recria",
        descricao="Fazenda que recria e confina animais",
        caracteristicas=[
            "Recria bezerros em pasto",
            "Confinamento para engorda final",
            "Otimização de custos",
            "Alta eficiência produtiva",
            "Controle de qualidade"
        ],
        categorias_principais=[
            "Bezerros", "Bezerras", "Garrotes", "Novilhas", "Bois"
        ],
        estrategia_vendas={
            "Bois": 0.95,
            "Garrotes": 0.85,
            "Novilhas": 0.80,
            "Bezerros": 0.70
        },
        estrategia_compras={
            "Bezerros": 0.70,
            "Bezerras": 0.30
        },
        parametros_producao={
            "natalidade": 0.00,
            "mortalidade_bezerros": 0.02,
            "mortalidade_adultos": 0.01,
            "ganho_peso_diario": 1.3,
            "idade_abate": 30,
            "peso_abate": 480,
            "periodo_confinamento": 90
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.16,
            "crescimento_receita_anual": 0.21,
            "margem_lucro_minima": 0.26
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 3500,
            "custo_por_animal_ano": 2600,
            "investimento_inicial_por_animal": 4000
        }
    ),

    TipoFazenda.CONFINAMENTO_ENGORDA: PerfilFazenda(
        tipo=TipoFazenda.CONFINAMENTO_ENGORDA,
        nome="Fazenda Confinamento + Engorda",
        descricao="Fazenda que compra animais para confinamento",
        caracteristicas=[
            "Compra animais para confinamento",
            "Sistema intensivo de engorda",
            "Alta produtividade",
            "Rotação rápida de capital",
            "Foco em eficiência alimentar"
        ],
        categorias_principais=[
            "Garrotes", "Novilhas", "Bois", "Bois Magros"
        ],
        estrategia_vendas={
            "Bois": 0.98,
            "Bois Magros": 0.97,
            "Garrotes": 0.95
        },
        estrategia_compras={
            "Garrotes": 0.70,
            "Novilhas": 0.30
        },
        parametros_producao={
            "natalidade": 0.00,
            "mortalidade_bezerros": 0.00,
            "mortalidade_adultos": 0.005,
            "ganho_peso_diario": 1.4,
            "idade_abate": 27,
            "peso_abate": 490,
            "periodo_confinamento": 100
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.14,
            "crescimento_receita_anual": 0.19,
            "margem_lucro_minima": 0.24
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 3800,
            "custo_por_animal_ano": 2800,
            "investimento_inicial_por_animal": 4500
        }
    ),

    TipoFazenda.CONFINAMENTO_COMPLETO: PerfilFazenda(
        tipo=TipoFazenda.CONFINAMENTO_COMPLETO,
        nome="Fazenda Confinamento Completo",
        descricao="Fazenda que realiza todo o ciclo em confinamento",
        caracteristicas=[
            "Ciclo completo em confinamento",
            "Máximo controle produtivo",
            "Alta produtividade",
            "Alto investimento",
            "Tecnologia avançada"
        ],
        categorias_principais=[
            "Multíparas", "Primíparas", "Novilhas", "Bezerras", "Bezerros", "Garrotes", "Bois"
        ],
        estrategia_vendas={
            "Bois": 0.90,
            "Garrotes": 0.85,
            "Bezerros": 0.80,
            "Vacas de Descarte": 0.95
        },
        estrategia_compras={
            "Novilhas": 0.70,
            "Multíparas": 0.30
        },
        parametros_producao={
            "natalidade": 0.85,
            "mortalidade_bezerros": 0.03,
            "mortalidade_adultos": 0.01,
            "ganho_peso_diario": 1.6,
            "idade_abate": 24,
            "peso_abate": 520,
            "periodo_confinamento": 120
        },
        metas_crescimento={
            "crescimento_rebanho_anual": 0.10,
            "crescimento_receita_anual": 0.15,
            "margem_lucro_minima": 0.20
        },
        indicadores_financeiros={
            "receita_por_animal_ano": 4500,
            "custo_por_animal_ano": 3500,
            "investimento_inicial_por_animal": 6000
        }
    )
}

def detectar_perfil_fazenda(inventario: Dict[str, int], parametros_usuario: Dict[str, Any]) -> TipoFazenda:
    """
    Detecta o perfil da fazenda baseado no inventário e parâmetros do usuário
    """
    # Análise do inventário
    total_animais = sum(inventario.values())
    
    # Cálculo de percentuais por categoria
    percentuais = {}
    for categoria, quantidade in inventario.items():
        if total_animais > 0:
            percentuais[categoria] = quantidade / total_animais
    
    # Lógica de detecção baseada em percentuais
    if percentuais.get('Multíparas', 0) > 0.3 and percentuais.get('Bois', 0) > 0.2:
        return TipoFazenda.CICLO_COMPLETO
    elif percentuais.get('Multíparas', 0) > 0.4 and percentuais.get('Bezerros', 0) > 0.3:
        return TipoFazenda.SO_CRIA
    elif percentuais.get('Bezerros', 0) > 0.4 and percentuais.get('Garrotes', 0) > 0.3:
        return TipoFazenda.SO_RECRIA
    elif percentuais.get('Garrotes', 0) > 0.4 and percentuais.get('Bois', 0) > 0.3:
        return TipoFazenda.SO_ENGORDA
    elif percentuais.get('Bezerros', 0) > 0.3 and percentuais.get('Bois', 0) > 0.2:
        return TipoFazenda.RECRIA_ENGORDA
    elif percentuais.get('Garrotes', 0) > 0.5 and percentuais.get('Bois', 0) > 0.4:
        return TipoFazenda.CONFINAMENTO
    elif percentuais.get('Bezerros', 0) > 0.3 and percentuais.get('Garrotes', 0) > 0.3:
        return TipoFazenda.CONFINAMENTO_RECRIA
    elif percentuais.get('Garrotes', 0) > 0.4 and percentuais.get('Bois', 0) > 0.5:
        return TipoFazenda.CONFINAMENTO_ENGORDA
    else:
        return TipoFazenda.CICLO_COMPLETO  # Padrão

def calcular_projecao_inteligente(perfil: PerfilFazenda, inventario: Dict[str, int], 
                                parametros_usuario: Dict[str, Any], anos: int = 5) -> Dict[str, Any]:
    """
    Calcula projeção inteligente baseada no perfil da fazenda
    """
    total_animais = sum(inventario.values())
    
    # Cálculos baseados no perfil
    receita_anual = total_animais * perfil.indicadores_financeiros['receita_por_animal_ano']
    despesa_anual = total_animais * perfil.indicadores_financeiros['custo_por_animal_ano']
    lucro_anual = receita_anual - despesa_anual
    
    # Projeção para múltiplos anos
    projecao = {
        'perfil_detectado': perfil.tipo.value,
        'nome_perfil': perfil.nome,
        'descricao': perfil.descricao,
        'anos_projecao': anos,
        'receita_total': 0,
        'despesa_total': 0,
        'lucro_total': 0,
        'crescimento_rebanho': 0,
        'anos_detalhados': []
    }
    
    rebanho_atual = total_animais
    receita_acumulada = 0
    despesa_acumulada = 0
    
    for ano in range(1, anos + 1):
        # Crescimento do rebanho
        crescimento_anual = rebanho_atual * perfil.metas_crescimento['crescimento_rebanho_anual']
        rebanho_atual += crescimento_anual
        
        # Receitas e despesas com inflação
        fator_inflacao = 1.05 ** ano  # 5% ao ano
        receita_ano = receita_anual * fator_inflacao
        despesa_ano = despesa_anual * fator_inflacao
        lucro_ano = receita_ano - despesa_ano
        
        receita_acumulada += receita_ano
        despesa_acumulada += despesa_ano
        
        projecao['anos_detalhados'].append({
            'ano': ano,
            'rebanho': int(rebanho_atual),
            'receita': receita_ano,
            'despesa': despesa_ano,
            'lucro': lucro_ano,
            'margem': (lucro_ano / receita_ano) * 100 if receita_ano > 0 else 0
        })
    
    projecao['receita_total'] = receita_acumulada
    projecao['despesa_total'] = despesa_acumulada
    projecao['lucro_total'] = receita_acumulada - despesa_acumulada
    projecao['crescimento_rebanho'] = ((rebanho_atual - total_animais) / total_animais) * 100
    
    return projecao

def gerar_recomendacoes_perfil(perfil: PerfilFazenda, projecao: Dict[str, Any]) -> List[str]:
    """
    Gera recomendações específicas para o perfil da fazenda
    """
    recomendacoes = []
    
    # Recomendações baseadas no perfil
    if perfil.tipo == TipoFazenda.SO_CRIA:
        recomendacoes.extend([
            "Foque na seleção genética das matrizes",
            "Mantenha alta taxa de natalidade",
            "Venda bezerros com 8-10 meses",
            "Invista em pastagens de qualidade"
        ])
    elif perfil.tipo == TipoFazenda.SO_ENGORDA:
        recomendacoes.extend([
            "Otimize a eficiência alimentar",
            "Mantenha rotação rápida de animais",
            "Monitore ganho de peso diário",
            "Invista em suplementação estratégica"
        ])
    elif perfil.tipo == TipoFazenda.CONFINAMENTO:
        recomendacoes.extend([
            "Controle rigoroso da alimentação",
            "Monitore saúde dos animais",
            "Otimize custos de ração",
            "Mantenha alta produtividade"
        ])
    
    # Recomendações baseadas na projeção
    if projecao['lucro_total'] < 0:
        recomendacoes.append("⚠️ Atenção: Projeção indica prejuízo. Revise custos e estratégias.")
    
    if projecao['crescimento_rebanho'] < 10:
        recomendacoes.append("📈 Considere estratégias para acelerar o crescimento do rebanho")
    
    return recomendacoes



