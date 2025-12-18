# -*- coding: utf-8 -*-
"""
Script para aplicar configuração padrão da Girassol na projeção PROJ-2025-0072
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual
)


def aplicar():
    """Aplica configuração padrão da Girassol"""
    
    print("=" * 80)
    print("APLICAR CONFIGURACAO PADRAO GIRASSOL PROJ-2025-0072")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0072'
    ).first()
    
    if not planejamento:
        print("\n[ERRO] Planejamento PROJ-2025-0072 não encontrado!")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Aplicar configuração padrão
    try:
        from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol
        aplicar_configuracao_padrao_girassol(girassol, planejamento)
        print("\n[SUCESSO] Configuracao padrao aplicada!")
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        aplicar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















