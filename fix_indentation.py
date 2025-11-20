#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problemas de indentação no arquivo views_exportacao.py
"""

import re

def fix_indentation():
    """Corrige problemas de indentação no arquivo views_exportacao.py"""
    
    file_path = 'gestao_rural/views_exportacao.py'
    
    try:
        # Ler o arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Arquivo lido com sucesso!")
        
        # Corrigir problemas específicos de indentação
        fixes = [
            # Corrigir linha 592 - indentação incorreta do if
            (r'(\s+)if i < len\(tabelas_divididas\) - 1:', r'            if i < len(tabelas_divididas) - 1:'),
            
            # Corrigir linha 593 - indentação incorreta do story.append
            (r'(\s+)story\.append\(PageBreak\(\)\)', r'                story.append(PageBreak())'),
            
            # Corrigir linha 596 - indentação incorreta do story.append
            (r'(\s+)story\.append\(PageBreak\(\)\)', r'        story.append(PageBreak())'),
        ]
        
        # Aplicar correções
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # Salvar o arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Arquivo corrigido com sucesso!")
        
        # Verificar sintaxe
        try:
            compile(content, file_path, 'exec')
            print("Sintaxe verificada - OK!")
            return True
        except SyntaxError as e:
            print(f"Erro de sintaxe ainda presente: {e}")
            return False
            
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        return False

if __name__ == "__main__":
    fix_indentation()

