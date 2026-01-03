# -*- coding: utf-8 -*-
"""
Validação de CPF e CNPJ
"""

import re


def validar_cpf(cpf: str) -> tuple[bool, str]:
    """
    Valida CPF verificando dígitos verificadores
    
    Args:
        cpf: CPF com ou sem formatação
        
    Returns:
        (valido, mensagem)
    """
    # Remove formatação
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return False, 'CPF deve ter 11 dígitos'
    
    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf_limpo == cpf_limpo[0] * 11:
        return False, 'CPF inválido (todos os dígitos iguais)'
    
    # Calcula primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf_limpo[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[9]) != digito1:
        return False, 'CPF inválido (dígito verificador incorreto)'
    
    # Calcula segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf_limpo[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[10]) != digito2:
        return False, 'CPF inválido (dígito verificador incorreto)'
    
    return True, 'CPF válido'


def validar_cnpj(cnpj: str) -> tuple[bool, str]:
    """
    Valida CNPJ verificando dígitos verificadores
    
    Args:
        cnpj: CNPJ com ou sem formatação
        
    Returns:
        (valido, mensagem)
    """
    # Remove formatação
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return False, 'CNPJ deve ter 14 dígitos'
    
    # Verifica se todos os dígitos são iguais (CNPJ inválido)
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False, 'CNPJ inválido (todos os dígitos iguais)'
    
    # Calcula primeiro dígito verificador
    tamanho = len(cnpj_limpo) - 2
    numeros = cnpj_limpo[:tamanho]
    digitos = cnpj_limpo[tamanho:]
    soma = 0
    pos = tamanho - 7
    
    for i in range(tamanho):
        soma += int(numeros[i]) * pos
        pos -= 1
        if pos < 2:
            pos = 9
    
    resultado = soma % 11
    digito1 = 0 if resultado < 2 else 11 - resultado
    
    if int(digitos[0]) != digito1:
        return False, 'CNPJ inválido (dígito verificador incorreto)'
    
    # Calcula segundo dígito verificador
    tamanho = tamanho + 1
    numeros = cnpj_limpo[:tamanho]
    soma = 0
    pos = tamanho - 7
    
    for i in range(tamanho):
        soma += int(numeros[i]) * pos
        pos -= 1
        if pos < 2:
            pos = 9
    
    resultado = soma % 11
    digito2 = 0 if resultado < 2 else 11 - resultado
    
    if int(digitos[1]) != digito2:
        return False, 'CNPJ inválido (dígito verificador incorreto)'
    
    return True, 'CNPJ válido'


def validar_cpf_cnpj(cpf_cnpj: str) -> tuple[bool, str, str]:
    """
    Valida CPF ou CNPJ
    
    Args:
        cpf_cnpj: CPF ou CNPJ
        
    Returns:
        (valido, tipo, mensagem) - tipo pode ser 'CPF', 'CNPJ' ou 'INVALIDO'
    """
    cpf_cnpj_limpo = re.sub(r'[^0-9]', '', cpf_cnpj)
    
    if len(cpf_cnpj_limpo) == 11:
        valido, mensagem = validar_cpf(cpf_cnpj)
        return valido, 'CPF', mensagem
    elif len(cpf_cnpj_limpo) == 14:
        valido, mensagem = validar_cnpj(cpf_cnpj)
        return valido, 'CNPJ', mensagem
    else:
        return False, 'INVALIDO', 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'

