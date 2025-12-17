# -*- coding: utf-8 -*-
"""
Script para verificar e limpar promoções incorretas de Vacas Descarte
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def aguardar_banco_livre(max_tentativas=30, intervalo=3):
    """Aguarda o banco de dados ficar livre"""
    for tentativa in range(max_tentativas):
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("ROLLBACK")
            return True
        except Exception:
            if tentativa < max_tentativas - 1:
                time.sleep(intervalo)
            else:
                return False
    return False


@transaction.atomic
def verificar_e_limpar():
    """Verifica e limpa promoções incorretas"""
    
    print("=" * 80)
    print("VERIFICAR E LIMPAR PROMOCOES INCORRETAS - VACAS DESCARTE")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento atual: {planejamento_atual.codigo}")
    
    # Buscar todas as promoções de entrada
    promocoes = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        planejamento=planejamento_atual
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Promocoes encontradas: {promocoes.count()}")
    
    promocoes_deletadas = 0
    
    for promocao in promocoes:
        print(f"  {promocao.data_movimentacao.strftime('%d/%m/%Y')}: +{promocao.quantidade} - {promocao.observacao}")
        
        # Verificar se há transferência correspondente após esta promoção
        transferencias_apos = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            data_movimentacao__gte=promocao.data_movimentacao,
            planejamento=planejamento_atual
        )
        
        if not transferencias_apos.exists():
            # Não há transferência após esta promoção, pode ser incorreta
            print(f"    [AVISO] Sem transferencia correspondente apos esta promocao")
            # Não deletar automaticamente, apenas avisar
    
    # Buscar promoções de saída correspondentes
    promocoes_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria__nome__icontains='Vacas em Reprodução',
        tipo_movimentacao='PROMOCAO_SAIDA',
        planejamento=planejamento_atual
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Promocoes de saida (Vacas em Reproducao): {promocoes_saida.count()}")
    
    for promocao_saida in promocoes_saida:
        print(f"  {promocao_saida.data_movimentacao.strftime('%d/%m/%Y')}: -{promocao_saida.quantidade} - {promocao_saida.observacao}")
    
    print(f"\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_limpar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











