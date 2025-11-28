# -*- coding: utf-8 -*-
"""
Template Tags para Formatação Brasileira
Números e moedas no padrão BR: 1.000,00
"""

import re
from django import template
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

register = template.Library()


@register.filter(name='data_br')
def data_br(valor):
    """
    Formata data no padrão brasileiro: dd/mm/yyyy
    Uso: {{ data|data_br }}
    """
    if valor is None or valor == '':
        return ''
    
    try:
        # Se for datetime, extrair apenas a data
        if isinstance(valor, datetime):
            return valor.date().strftime('%d/%m/%Y')
        
        # Se for date, formatar diretamente
        if isinstance(valor, date):
            return valor.strftime('%d/%m/%Y')
        
        # Se for string, tentar converter
        if isinstance(valor, str):
            # Se já estiver no formato brasileiro, retornar
            if '/' in valor and len(valor.split('/')) == 3:
                return valor
            
            # Tentar converter string para date/datetime
            for formato in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                try:
                    data_obj = datetime.strptime(valor, formato)
                    return data_obj.date().strftime('%d/%m/%Y')
                except ValueError:
                    continue
        
        # Se não conseguir converter, retornar string original
        return str(valor)
    
    except (ValueError, TypeError, AttributeError):
        return ''


@register.filter(name='data_br')
def data_br(valor):
    """
    Formata data no padrão brasileiro: dd/mm/yyyy
    Uso: {{ data|data_br }}
    """
    if valor is None or valor == '':
        return '-'
    
    try:
        # Se já for uma data (date ou datetime)
        if isinstance(valor, (date, datetime)):
            return valor.strftime('%d/%m/%Y')
        
        # Se for string, tentar converter
        if isinstance(valor, str):
            # Tentar vários formatos comuns
            formatos = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y',
                '%d-%m-%Y',
            ]
            for formato in formatos:
                try:
                    data_obj = datetime.strptime(valor, formato)
                    return data_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
        
        return str(valor)
    
    except (ValueError, TypeError, AttributeError):
        return '-'


@register.filter(name='moeda_br')
def moeda_br(valor):
    """
    Formata valor como moeda brasileira: R$ 1.000,00
    Uso: {{ valor|moeda_br }}
    """
    if valor is None or valor == '':
        return 'R$ 0,00'
    
    try:
        # Converter para Decimal
        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '.')
        
        valor_decimal = Decimal(str(valor))
        
        # Formatar com separadores brasileiros
        # Parte inteira
        parte_inteira = int(abs(valor_decimal))
        parte_decimal = abs(valor_decimal) - parte_inteira
        
        # Formatar parte inteira com pontos
        parte_inteira_formatada = f'{parte_inteira:,}'.replace(',', '.')
        
        # Formatar parte decimal com 2 casas
        parte_decimal_formatada = f'{parte_decimal:.2f}'.split('.')[1]
        
        # Juntar
        valor_formatado = f'{parte_inteira_formatada},{parte_decimal_formatada}'
        
        # Adicionar sinal negativo se necessário
        if valor_decimal < 0:
            valor_formatado = f'-{valor_formatado}'
        
        return f'R$ {valor_formatado}'
    
    except (ValueError, TypeError, AttributeError):
        return 'R$ 0,00'


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtém um item de um dicionário pelo nome da chave"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


@register.filter(name='numero_br')
def numero_br(valor, casas_decimais=0):
    """
    Formata número no padrão brasileiro: 1.000 ou 1.152,38
    Uso: {{ valor|numero_br }} ou {{ valor|numero_br:2 }}
    """
    if valor is None or valor == '':
        return '0'
    
    try:
        # Converter para float/Decimal
        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '.')
        
        valor_decimal = Decimal(str(valor))
        
        # Se tem casas decimais especificadas
        if casas_decimais > 0:
            # Parte inteira
            parte_inteira = int(abs(valor_decimal))
            
            # Formatar parte inteira com pontos
            parte_inteira_formatada = f'{parte_inteira:,}'.replace(',', '.')
            
            # Parte decimal
            formato_decimal = f'{{:.{casas_decimais}f}}'
            parte_decimal = formato_decimal.format(abs(valor_decimal) - parte_inteira).split('.')[1]
            
            valor_formatado = f'{parte_inteira_formatada},{parte_decimal}'
        else:
            # Apenas parte inteira
            parte_inteira = int(abs(valor_decimal))
            valor_formatado = f'{parte_inteira:,}'.replace(',', '.')
        
        # Adicionar sinal negativo se necessário
        if valor_decimal < 0:
            valor_formatado = f'-{valor_formatado}'
        
        return valor_formatado
    
    except (ValueError, TypeError, AttributeError):
        return '0'


@register.filter(name='percentual_br')
def percentual_br(valor, casas_decimais=1):
    """
    Formata percentual no padrão brasileiro: 23,5%
    Uso: {{ valor|percentual_br }} ou {{ valor|percentual_br:2 }}
    """
    if valor is None or valor == '':
        return '0%'
    
    try:
        valor_decimal = Decimal(str(valor))
        
        # Formatar com casas decimais
        formato = f'{{:.{casas_decimais}f}}'
        valor_formatado = formato.format(float(valor_decimal)).replace('.', ',')
        
        return f'{valor_formatado}%'
    
    except (ValueError, TypeError, AttributeError):
        return '0%'


@register.filter(name='numero_abreviado')
def numero_abreviado(valor):
    """
    Abrevia números grandes: 1.5k, 2.3M
    Uso: {{ valor|numero_abreviado }}
    """
    if valor is None or valor == '':
        return '0'
    
    try:
        valor_float = float(valor)
        
        if abs(valor_float) >= 1000000000:
            return f'{valor_float/1000000000:.1f}B'.replace('.', ',')
        elif abs(valor_float) >= 1000000:
            return f'{valor_float/1000000:.1f}M'.replace('.', ',')
        elif abs(valor_float) >= 1000:
            return f'{valor_float/1000:.1f}k'.replace('.', ',')
        else:
            return numero_br(valor_float, 0)
    
    except (ValueError, TypeError):
        return '0'


@register.simple_tag
def moeda_com_classe(valor, mostrar_positivo=True):
    """
    Formata moeda com classe CSS para positivo/negativo
    Uso: {% moeda_com_classe valor %}
    """
    try:
        valor_decimal = Decimal(str(valor))
        moeda_formatada = moeda_br(valor_decimal)
        
        if valor_decimal > 0 and mostrar_positivo:
            classe = 'text-success'
            icone = '<i class="fas fa-arrow-up"></i> '
        elif valor_decimal < 0:
            classe = 'text-danger'
            icone = '<i class="fas fa-arrow-down"></i> '
        else:
            classe = 'text-muted'
            icone = ''
        
        return f'<span class="{classe}">{icone}{moeda_formatada}</span>'
    
    except (ValueError, TypeError, AttributeError, InvalidOperation):
        return '<span class="text-muted">R$ 0,00</span>'


@register.simple_tag
def variacao_percentual(valor_atual, valor_anterior):
    """
    Calcula e formata variação percentual com cor
    Uso: {% variacao_percentual 1500 1200 %}
    """
    try:
        atual = Decimal(str(valor_atual))
        anterior = Decimal(str(valor_anterior))
        
        if anterior == 0:
            return '<span class="text-muted">-</span>'
        
        variacao = ((atual - anterior) / anterior) * 100
        variacao_formatada = percentual_br(variacao, 1)
        
        if variacao > 0:
            classe = 'text-success'
            icone = '<i class="fas fa-arrow-up"></i> +'
        elif variacao < 0:
            classe = 'text-danger'
            icone = '<i class="fas fa-arrow-down"></i> '
            variacao_formatada = variacao_formatada.replace('-', '')
        else:
            classe = 'text-muted'
            icone = ''
        
        return f'<span class="{classe}">{icone}{variacao_formatada}</span>'
    
    except (ValueError, TypeError, AttributeError, ZeroDivisionError, InvalidOperation):
        return '<span class="text-muted">-</span>'


@register.filter(name='dict_get')
def dict_get(mapping, key):
    """Permite acessar itens de dicionários nos templates."""
    if isinstance(mapping, dict):
        return mapping.get(key)
    return None


@register.filter(name='extrair_manejo_sisbov')
def extrair_manejo_sisbov(codigo_sisbov):
    """
    Extrai o número de manejo SISBOV do código completo.
    
    Para códigos SISBOV de 15 dígitos, extrai os dígitos das posições 8-13 (6 dígitos).
    Exemplo: 105500376197505 -> 619750
    
    Uso: {{ animal.codigo_sisbov|extrair_manejo_sisbov }}
    """
    if not codigo_sisbov:
        return ''
    
    # Remove caracteres não numéricos
    codigo_limpo = re.sub(r'\D', '', str(codigo_sisbov))
    
    if len(codigo_limpo) == 15:
        # Código SISBOV completo: extrair posições 8-13 (6 dígitos)
        return codigo_limpo[8:14]
    elif len(codigo_limpo) >= 8:
        # Lógica para códigos menores: 7 últimos dígitos sem o verificador
        return codigo_limpo[:-1][-7:]
    
    return ''


@register.filter(name='div')
def div(valor, divisor):
    """
    Divide um valor por outro.
    Uso: {{ valor|div:divisor }}
    Exemplo: {{ 100|div:2 }} retorna 50.0
    """
    try:
        if valor is None or divisor is None:
            return 0
        
        valor_decimal = Decimal(str(valor))
        divisor_decimal = Decimal(str(divisor))
        
        if divisor_decimal == 0:
            return 0
        
        resultado = valor_decimal / divisor_decimal
        return float(resultado)
    
    except (ValueError, TypeError, AttributeError, InvalidOperation, ZeroDivisionError):
        return 0


@register.filter(name='mul')
def mul(valor, multiplicador):
    """
    Multiplica um valor por outro.
    Uso: {{ valor|mul:multiplicador }}
    Exemplo: {{ 100|mul:2 }} retorna 200.0
    """
    try:
        if valor is None or multiplicador is None:
            return 0
        
        valor_decimal = Decimal(str(valor))
        multiplicador_decimal = Decimal(str(multiplicador))
        
        resultado = valor_decimal * multiplicador_decimal
        return float(resultado)
    
    except (ValueError, TypeError, AttributeError, InvalidOperation):
        return 0