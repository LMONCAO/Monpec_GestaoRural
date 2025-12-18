# -*- coding: utf-8 -*-
"""
Script para deletar transferências de garrotes de 2024, 2025, 2026
pois não há arrendamento nesses anos
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal
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
def deletar_transferencias_2024_2025_2026():
    """Deleta transferências de garrotes de 2024, 2025, 2026"""
    
    print("=" * 80)
    print("DELETAR TRANSFERENCIAS 2024, 2025, 2026")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    # Deletar transferências de saída da Canta Galo
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar transferências de entrada no Favo de Mel
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar transferências de saída do Favo de Mel
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar transferências de entrada no Girassol
    entradas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar evoluções relacionadas
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    evolucoes_saida = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2025, 2026, 2027]  # Evoluções acontecem 12 meses depois
    )
    
    evolucoes_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi,
        data_movimentacao__year__in=[2025, 2026, 2027]
    )
    
    # Deletar vendas relacionadas
    vendas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao__year__in=[2025, 2026, 2027, 2028]  # Vendas acontecem 90 dias após evolução
    )
    
    total_deletado = (
        saidas_canta.count() + 
        entradas_favo.count() + 
        saidas_favo.count() + 
        entradas_girassol.count() +
        evolucoes_saida.count() +
        evolucoes_entrada.count() +
        vendas_girassol.count()
    )
    
    print(f"\n[INFO] Movimentacoes a deletar: {total_deletado}")
    print(f"   Saidas Canta Galo: {saidas_canta.count()}")
    print(f"   Entradas Favo de Mel: {entradas_favo.count()}")
    print(f"   Saidas Favo de Mel: {saidas_favo.count()}")
    print(f"   Entradas Girassol: {entradas_girassol.count()}")
    print(f"   Evolucoes: {evolucoes_saida.count() + evolucoes_entrada.count()}")
    print(f"   Vendas Girassol: {vendas_girassol.count()}")
    
    # Deletar vendas projetadas
    from gestao_rural.models import VendaProjetada
    vendas_projetadas = VendaProjetada.objects.filter(
        movimentacao_projetada__in=vendas_girassol
    )
    vendas_projetadas.delete()
    
    # Deletar todas as movimentações
    vendas_girassol.delete()
    evolucoes_entrada.delete()
    evolucoes_saida.delete()
    entradas_girassol.delete()
    saidas_favo.delete()
    entradas_favo.delete()
    saidas_canta.delete()
    
    print(f"\n[OK] {total_deletado} movimentacoes deletadas")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        deletar_transferencias_2024_2025_2026()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















