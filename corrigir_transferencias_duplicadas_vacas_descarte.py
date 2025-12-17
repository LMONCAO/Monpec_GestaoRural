# -*- coding: utf-8 -*-
"""
Script para corrigir transferências duplicadas de vacas descarte no Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal


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
def corrigir_transferencias_duplicadas():
    """Remove transferências duplicadas de vacas descarte"""
    
    print("=" * 60)
    print("CORRIGIR TRANSFERENCIAS DUPLICADAS VACAS DESCARTE")
    print("=" * 60)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar todas as transferências de entrada de vacas descarte
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        observacao__icontains='Transferencia automatica'
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias automaticas encontradas: {transferencias.count()}")
    
    # Agrupar por data para identificar duplicatas
    transferencias_por_data = {}
    for t in transferencias:
        data_key = t.data_movimentacao
        if data_key not in transferencias_por_data:
            transferencias_por_data[data_key] = []
        transferencias_por_data[data_key].append(t)
    
    total_deletadas = 0
    
    for data_key, lista_transferencias in transferencias_por_data.items():
        if len(lista_transferencias) > 1:
            print(f"\n[INFO] Duplicatas encontradas para {data_key.strftime('%d/%m/%Y')}: {len(lista_transferencias)} transferencias")
            
            # Manter apenas a primeira, deletar as outras
            primeira = lista_transferencias[0]
            print(f"   Mantendo: ID {primeira.id} (planejamento: {primeira.planejamento.codigo if primeira.planejamento else 'None'})")
            
            for t in lista_transferencias[1:]:
                print(f"   Deletando: ID {t.id} (planejamento: {t.planejamento.codigo if t.planejamento else 'None'})")
                t.delete()
                total_deletadas += 1
    
    # Verificar se há transferências que não deveriam existir
    # As vacas descarte não deveriam ser transferidas para Favo de Mel
    # Elas deveriam ir para Invernada Grande
    print(f"\n[INFO] Verificando se essas transferencias deveriam existir...")
    
    # Buscar planejamento atual
    from gestao_rural.models import PlanejamentoAnual
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if planejamento_atual:
        print(f"   Planejamento atual: {planejamento_atual.codigo}")
        
        # Deletar todas as transferências de vacas descarte do Favo de Mel
        # pois elas não deveriam estar lá
        transferencias_restantes = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte
        )
        
        if transferencias_restantes.exists():
            print(f"\n[INFO] Deletando todas as transferencias de vacas descarte do Favo de Mel")
            print(f"   (Elas nao deveriam estar aqui, deveriam ir para Invernada Grande)")
            quantidade_deletar = transferencias_restantes.count()
            transferencias_restantes.delete()
            total_deletadas += quantidade_deletar
            print(f"   [OK] {quantidade_deletar} transferencias deletadas")
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de transferencias deletadas: {total_deletadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias_duplicadas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











