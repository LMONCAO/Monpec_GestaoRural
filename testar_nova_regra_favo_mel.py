# -*- coding: utf-8 -*-
"""
Script para testar a nova regra do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, PlanejamentoAnual
from gestao_rural.configuracao_padrao_favo_mel import aplicar_configuracao_padrao_favo_mel

def testar():
    """Testa a nova regra"""
    
    print("=" * 80)
    print("TESTAR NOVA REGRA FAVO DE MEL")
    print("=" * 80)
    print("Nova regra: Valor vendido de bezerras fêmeas (0-12 meses)")
    print("            vira compra de garrotes (machos 12-24 meses)")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    try:
        aplicar_configuracao_padrao_favo_mel(favo_mel, planejamento)
        print("\n[SUCESSO] Nova regra aplicada!")
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    testar()










