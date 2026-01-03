# -*- coding: utf-8 -*-
"""
Script para criar projeções do Favo de Mel para 2022, 2023, 2024 e 2025
Baseado nas transferências de entrada da Canta Galo e saídas para Girassol
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
def criar_projecoes_favo_mel():
    """Cria projeções do Favo de Mel para 2022-2025"""
    
    print("=" * 80)
    print("CRIAR PROJECOES FAVO DE MEL 2022-2025")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_favo:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento: {planejamento_favo.codigo}")
    
    # Verificar entradas (da Canta Galo)
    entradas = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Entradas encontradas: {entradas.count()}")
    
    # Verificar saídas (para Girassol)
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"[INFO] Saidas encontradas: {saidas.count()}")
    
    # Verificar se todas as entradas e saídas estão vinculadas ao planejamento atual
    entradas_sem_planejamento = entradas.exclude(planejamento=planejamento_favo)
    saidas_sem_planejamento = saidas.exclude(planejamento=planejamento_favo)
    
    if entradas_sem_planejamento.exists():
        print(f"\n[INFO] Vinculando {entradas_sem_planejamento.count()} entradas ao planejamento atual")
        entradas_sem_planejamento.update(planejamento=planejamento_favo)
    
    if saidas_sem_planejamento.exists():
        print(f"[INFO] Vinculando {saidas_sem_planejamento.count()} saidas ao planejamento atual")
        saidas_sem_planejamento.update(planejamento=planejamento_favo)
    
    # Verificar por ano
    anos = [2022, 2023, 2024, 2025]
    
    print(f"\n[VERIFICACAO POR ANO]")
    for ano in anos:
        entradas_ano = entradas.filter(data_movimentacao__year=ano)
        saidas_ano = saidas.filter(data_movimentacao__year=ano)
        
        total_entradas = sum(e.quantidade for e in entradas_ano)
        total_saidas = sum(s.quantidade for s in saidas_ano)
        
        print(f"\n  {ano}:")
        print(f"    Entradas: {entradas_ano.count()} ({total_entradas} garrotes)")
        print(f"    Saidas: {saidas_ano.count()} ({total_saidas} garrotes)")
        
        if entradas_ano.exists() or saidas_ano.exists():
            # Vincular ao planejamento atual
            entradas_ano.update(planejamento=planejamento_favo)
            saidas_ano.update(planejamento=planejamento_favo)
            print(f"    [OK] Movimentacoes vinculadas ao planejamento atual")
    
    # Verificar resultado final
    movimentacoes_finais = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        planejamento=planejamento_favo
    )
    
    print(f"\n[RESUMO FINAL]")
    print(f"  Total de movimentacoes no planejamento atual: {movimentacoes_finais.count()}")
    
    tipos = movimentacoes_finais.values_list('tipo_movimentacao', flat=True).distinct()
    for tipo in tipos:
        count = movimentacoes_finais.filter(tipo_movimentacao=tipo).count()
        print(f"    {tipo}: {count}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_projecoes_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























