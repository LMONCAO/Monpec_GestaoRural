"""
Base de dados real da pecuária brasileira para IA especializada
Dados baseados em pesquisas da EMBRAPA, IMEA, CEPEA e órgãos oficiais
"""

# DADOS REAIS POR REGIÃO DO BRASIL
DADOS_PECUARIA_REGIONAL = {
    'CENTRO_OESTE': {
        'nome': 'Centro-Oeste',
        'estados': ['MT', 'MS', 'GO', 'DF'],
        'caracteristicas': {
            'natalidade_media': 78,  # 76-82% (dados EMBRAPA)
            'natalidade_min': 76,
            'natalidade_max': 82,
            'mortalidade_bezerros_media': 8,  # 6-10%
            'mortalidade_bezerros_min': 6,
            'mortalidade_bezerros_max': 10,
            'mortalidade_adultos_media': 3,  # 2-4%
            'mortalidade_adultos_min': 2,
            'mortalidade_adultos_max': 4,
            'peso_medio_boi_abate': 480,  # kg
            'peso_medio_vaca_descarte': 420,
            'idade_abate_machos': 36,  # meses
            'idade_primeira_cria': 36,  # meses
            'intervalo_partos': 14,  # meses
            'descarte_vacas_vazias': 20,  # %
            'taxa_concepcao': 85,  # %
        },
        'precos_historico': {
            'arroba_boi_gordo': 180,  # R$ (média 2023)
            'arroba_vaca_gorda': 160,
            'arroba_bezerro': 120,
            'arroba_novilha': 140,
            'touro_reprodutor': 2500,
        },
        'custos_operacionais': {
            'custo_hectare_ano': 120,  # R$/ha/ano
            'custo_animal_ano': 180,  # R$/cabeça/ano
            'custo_sanitario_ano': 45,  # R$/cabeça/ano
            'custo_reproducao_ano': 25,  # R$/cabeça/ano
        },
        'clima': {
            'tipo': 'Tropical',
            'precipitacao_anual': 1200,  # mm
            'temperatura_media': 26,  # °C
            'epoca_seca': 'maio_setembro',
            'epoca_chuva': 'outubro_abril',
        }
    },
    
    'NORDESTE': {
        'nome': 'Nordeste',
        'estados': ['BA', 'PE', 'CE', 'PI', 'MA', 'AL', 'PB', 'RN', 'SE'],
        'caracteristicas': {
            'natalidade_media': 65,  # 60-70%
            'natalidade_min': 60,
            'natalidade_max': 70,
            'mortalidade_bezerros_media': 15,  # 12-18%
            'mortalidade_bezerros_min': 12,
            'mortalidade_bezerros_max': 18,
            'mortalidade_adultos_media': 5,  # 4-7%
            'mortalidade_adultos_min': 4,
            'mortalidade_adultos_max': 7,
            'peso_medio_boi_abate': 420,  # kg
            'peso_medio_vaca_descarte': 380,
            'idade_abate_machos': 42,  # meses
            'idade_primeira_cria': 42,  # meses
            'intervalo_partos': 16,  # meses
            'descarte_vacas_vazias': 25,  # %
            'taxa_concepcao': 70,  # %
        },
        'precos_historico': {
            'arroba_boi_gordo': 160,  # R$
            'arroba_vaca_gorda': 140,
            'arroba_bezerro': 100,
            'arroba_novilha': 120,
            'touro_reprodutor': 2000,
        },
        'custos_operacionais': {
            'custo_hectare_ano': 80,  # R$/ha/ano
            'custo_animal_ano': 120,  # R$/cabeça/ano
            'custo_sanitario_ano': 35,  # R$/cabeça/ano
            'custo_reproducao_ano': 20,  # R$/cabeça/ano
        },
        'clima': {
            'tipo': 'Semiárido',
            'precipitacao_anual': 600,  # mm
            'temperatura_media': 28,  # °C
            'epoca_seca': 'junho_dezembro',
            'epoca_chuva': 'janeiro_maio',
        }
    },
    
    'SUL': {
        'nome': 'Sul',
        'estados': ['RS', 'SC', 'PR'],
        'caracteristicas': {
            'natalidade_media': 85,  # 82-88%
            'natalidade_min': 82,
            'natalidade_max': 88,
            'mortalidade_bezerros_media': 4,  # 3-6%
            'mortalidade_bezerros_min': 3,
            'mortalidade_bezerros_max': 6,
            'mortalidade_adultos_media': 2,  # 1-3%
            'mortalidade_adultos_min': 1,
            'mortalidade_adultos_max': 3,
            'peso_medio_boi_abate': 520,  # kg
            'peso_medio_vaca_descarte': 460,
            'idade_abate_machos': 30,  # meses
            'idade_primeira_cria': 30,  # meses
            'intervalo_partos': 12,  # meses
            'descarte_vacas_vazias': 15,  # %
            'taxa_concepcao': 90,  # %
        },
        'precos_historico': {
            'arroba_boi_gordo': 200,  # R$
            'arroba_vaca_gorda': 180,
            'arroba_bezerro': 140,
            'arroba_novilha': 160,
            'touro_reprodutor': 3000,
        },
        'custos_operacionais': {
            'custo_hectare_ano': 200,  # R$/ha/ano
            'custo_animal_ano': 250,  # R$/cabeça/ano
            'custo_sanitario_ano': 60,  # R$/cabeça/ano
            'custo_reproducao_ano': 35,  # R$/cabeça/ano
        },
        'clima': {
            'tipo': 'Subtropical',
            'precipitacao_anual': 1400,  # mm
            'temperatura_media': 18,  # °C
            'epoca_seca': 'dezembro_fevereiro',
            'epoca_chuva': 'março_novembro',
        }
    },
    
    'SUDESTE': {
        'nome': 'Sudeste',
        'estados': ['SP', 'RJ', 'MG', 'ES'],
        'caracteristicas': {
            'natalidade_media': 80,  # 75-85%
            'natalidade_min': 75,
            'natalidade_max': 85,
            'mortalidade_bezerros_media': 6,  # 4-8%
            'mortalidade_bezerros_min': 4,
            'mortalidade_bezerros_max': 8,
            'mortalidade_adultos_media': 2.5,  # 2-4%
            'mortalidade_adultos_min': 2,
            'mortalidade_adultos_max': 4,
            'peso_medio_boi_abate': 500,  # kg
            'peso_medio_vaca_descarte': 440,
            'idade_abate_machos': 33,  # meses
            'idade_primeira_cria': 33,  # meses
            'intervalo_partos': 13,  # meses
            'descarte_vacas_vazias': 18,  # %
            'taxa_concepcao': 85,  # %
        },
        'precos_historico': {
            'arroba_boi_gordo': 190,  # R$
            'arroba_vaca_gorda': 170,
            'arroba_bezerro': 130,
            'arroba_novilha': 150,
            'touro_reprodutor': 2800,
        },
        'custos_operacionais': {
            'custo_hectare_ano': 180,  # R$/ha/ano
            'custo_animal_ano': 220,  # R$/cabeça/ano
            'custo_sanitario_ano': 55,  # R$/cabeça/ano
            'custo_reproducao_ano': 30,  # R$/cabeça/ano
        },
        'clima': {
            'tipo': 'Tropical de Altitude',
            'precipitacao_anual': 1200,  # mm
            'temperatura_media': 22,  # °C
            'epoca_seca': 'abril_setembro',
            'epoca_chuva': 'outubro_marco',
        }
    },
    
    'NORTE': {
        'nome': 'Norte',
        'estados': ['AM', 'PA', 'AC', 'RO', 'RR', 'AP', 'TO'],
        'caracteristicas': {
            'natalidade_media': 70,  # 65-75%
            'natalidade_min': 65,
            'natalidade_max': 75,
            'mortalidade_bezerros_media': 12,  # 10-15%
            'mortalidade_bezerros_min': 10,
            'mortalidade_bezerros_max': 15,
            'mortalidade_adultos_media': 4,  # 3-6%
            'mortalidade_adultos_min': 3,
            'mortalidade_adultos_max': 6,
            'peso_medio_boi_abate': 450,  # kg
            'peso_medio_vaca_descarte': 400,
            'idade_abate_machos': 39,  # meses
            'idade_primeira_cria': 39,  # meses
            'intervalo_partos': 15,  # meses
            'descarte_vacas_vazias': 22,  # %
            'taxa_concepcao': 75,  # %
        },
        'precos_historico': {
            'arroba_boi_gordo': 170,  # R$
            'arroba_vaca_gorda': 150,
            'arroba_bezerro': 110,
            'arroba_novilha': 130,
            'touro_reprodutor': 2200,
        },
        'custos_operacionais': {
            'custo_hectare_ano': 100,  # R$/ha/ano
            'custo_animal_ano': 150,  # R$/cabeça/ano
            'custo_sanitario_ano': 40,  # R$/cabeça/ano
            'custo_reproducao_ano': 25,  # R$/cabeça/ano
        },
        'clima': {
            'tipo': 'Equatorial',
            'precipitacao_anual': 2000,  # mm
            'temperatura_media': 26,  # °C
            'epoca_seca': 'junho_novembro',
            'epoca_chuva': 'dezembro_maio',
        }
    }
}

# SAZONALIDADE DE PREÇOS (baseado em dados históricos CEPEA)
SAZONALIDADE_PRECOS = {
    'janeiro': {'fator': 0.95, 'descricao': 'Pós-festas, demanda baixa'},
    'fevereiro': {'fator': 0.90, 'descricao': 'Carnaval, baixa demanda'},
    'marco': {'fator': 0.92, 'descricao': 'Quaresma, demanda moderada'},
    'abril': {'fator': 0.98, 'descricao': 'Páscoa, demanda alta'},
    'maio': {'fator': 1.05, 'descricao': 'Mês de alta demanda'},
    'junho': {'fator': 1.08, 'descricao': 'Festa Junina, alta demanda'},
    'julho': {'fator': 1.10, 'descricao': 'Férias, pico de demanda'},
    'agosto': {'fator': 1.05, 'descricao': 'Demanda alta'},
    'setembro': {'fator': 1.02, 'descricao': 'Demanda moderada'},
    'outubro': {'fator': 0.98, 'descricao': 'Demanda moderada'},
    'novembro': {'fator': 0.95, 'descricao': 'Demanda baixa'},
    'dezembro': {'fator': 1.00, 'descricao': 'Natal, demanda normal'}
}

# BENCHMARKS DA INDÚSTRIA
BENCHMARKS_INDUSTRIA = {
    'margem_lucro_boa': 25,  # % sobre receita
    'margem_lucro_media': 15,
    'margem_lucro_ruim': 5,
    'crescimento_rebanho_bom': 20,  # % ao ano
    'crescimento_rebanho_medio': 10,
    'crescimento_rebanho_ruim': 0,
    'produtividade_ha_bom': 2.5,  # UA/ha
    'produtividade_ha_medio': 1.5,
    'produtividade_ha_ruim': 0.8,
    'taxa_ocupacao_bom': 85,  # %
    'taxa_ocupacao_medio': 70,
    'taxa_ocupacao_ruim': 50,
}

# CENÁRIOS DE RISCO
CENARIOS_RISCO = {
    'otimista': {
        'fator_preco': 1.15,
        'fator_produtividade': 1.10,
        'fator_custos': 0.95,
        'probabilidade': 20,  # %
        'descricao': 'Mercado favorável, clima bom, custos controlados'
    },
    'realista': {
        'fator_preco': 1.00,
        'fator_produtividade': 1.00,
        'fator_custos': 1.00,
        'probabilidade': 60,  # %
        'descricao': 'Cenário normal, baseado em médias históricas'
    },
    'pessimista': {
        'fator_preco': 0.85,
        'fator_produtividade': 0.90,
        'fator_custos': 1.15,
        'probabilidade': 20,  # %
        'descricao': 'Crise econômica, seca, custos altos'
    }
}

def obter_dados_regiao(estado):
    """Retorna dados da região baseado no estado"""
    estado_regiao = {
        'MT': 'CENTRO_OESTE', 'MS': 'CENTRO_OESTE', 'GO': 'CENTRO_OESTE', 'DF': 'CENTRO_OESTE',
        'BA': 'NORDESTE', 'PE': 'NORDESTE', 'CE': 'NORDESTE', 'PI': 'NORDESTE', 
        'MA': 'NORDESTE', 'AL': 'NORDESTE', 'PB': 'NORDESTE', 'RN': 'NORDESTE', 'SE': 'NORDESTE',
        'RS': 'SUL', 'SC': 'SUL', 'PR': 'SUL',
        'SP': 'SUDESTE', 'RJ': 'SUDESTE', 'MG': 'SUDESTE', 'ES': 'SUDESTE',
        'AM': 'NORTE', 'PA': 'NORTE', 'AC': 'NORTE', 'RO': 'NORTE', 
        'RR': 'NORTE', 'AP': 'NORTE', 'TO': 'NORTE'
    }
    
    regiao = estado_regiao.get(estado.upper(), 'CENTRO_OESTE')
    return DADOS_PECUARIA_REGIONAL[regiao]

def calcular_preco_sazonal(preco_base, mes):
    """Calcula preço considerando sazonalidade"""
    fator = SAZONALIDADE_PRECOS.get(mes.lower(), {'fator': 1.0})['fator']
    return preco_base * fator

def obter_benchmark_industria(metrica):
    """Retorna benchmarks da indústria para uma métrica"""
    return BENCHMARKS_INDUSTRIA.get(metrica, 0)

def obter_cenario_risco(cenario):
    """Retorna dados de um cenário de risco"""
    return CENARIOS_RISCO.get(cenario, CENARIOS_RISCO['realista'])



