# -*- coding: utf-8 -*-
"""
Script para aplicar configuração padrão da Girassol manualmente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, PlanejamentoAnual
from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol

def aplicar():
    """Aplica configuração padrão da Girassol"""
    
    print("=" * 80)
    print("APLICAR CONFIGURACAO PADRAO GIRASSOL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    try:
        aplicar_configuracao_padrao_girassol(girassol, planejamento)
        print("\n[SUCESSO] Configuracao padrao aplicada!")
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    aplicar()











