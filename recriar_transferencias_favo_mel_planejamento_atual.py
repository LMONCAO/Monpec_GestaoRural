# -*- coding: utf-8 -*-
"""
Script para recriar as transferências de entrada no Favo de Mel vinculadas ao planejamento atual
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
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual
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
def recriar_transferencias_favo_mel():
    """Recria transferências de entrada no Favo de Mel vinculadas ao planejamento atual"""
    
    print("=" * 60)
    print("RECRIAR TRANSFERENCIAS FAVO DE MEL")
    print("=" * 60)
    
    # Buscar propriedades
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        print(f"\n[OK] Propriedades encontradas")
    except:
        print("[ERRO] Propriedades nao encontradas")
        return
    
    # Buscar categoria
    try:
        categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        print(f"[OK] Categoria: {categoria.nome}")
    except:
        print("[ERRO] Categoria nao encontrada")
        return
    
    # Buscar planejamento atual do Favo de Mel
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_favo:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[OK] Planejamento Favo de Mel: {planejamento_favo.codigo} (ano {planejamento_favo.ano})")
    
    # Buscar transferências de saída da Canta Galo
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria,
        data_movimentacao__year__in=[2022, 2023, 2024, 2025, 2026]
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de SAIDA da Canta Galo encontradas: {transferencias_saida.count()}")
    
    transferencias_criadas = 0
    
    for saida in transferencias_saida:
        data_transferencia = saida.data_movimentacao
        quantidade = saida.quantidade
        
        # Verificar se já existe transferência de entrada no Favo de Mel para esta data
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria,
            data_movimentacao=data_transferencia,
            planejamento=planejamento_favo
        ).first()
        
        if entrada_existente:
            print(f"   [INFO] Transferencia ja existe: {quantidade} em {data_transferencia.strftime('%d/%m/%Y')}")
        else:
            # Criar transferência de entrada
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento_favo,
                observacao=f'Transferencia de Canta Galo - {quantidade} garrotes (ano {data_transferencia.year})'
            )
            print(f"   [OK] Transferencia criada: {quantidade} em {data_transferencia.strftime('%d/%m/%Y')}")
            transferencias_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas: {transferencias_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        recriar_transferencias_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










