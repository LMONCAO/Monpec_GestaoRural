# -*- coding: utf-8 -*-
"""
Script para corrigir saldo negativo da Invernada Grande em 2025
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
def corrigir_saldo_negativo():
    """Corrige saldo negativo deletando movimentações incorretas"""
    
    print("=" * 80)
    print("CORRIGIR SALDO NEGATIVO INVERNADA GRANDE - 2025")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar planejamento atual
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar TODAS as movimentações
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    print(f"\n[INFO] Total de movimentacoes: {todas_movimentacoes.count()}")
    
    # Listar todas as movimentações
    print(f"\n[MOVIMENTACOES]")
    for mov in todas_movimentacoes:
        print(f"  {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.tipo_movimentacao} {mov.quantidade:+d} - {mov.observacao[:50]}")
    
    # Calcular saldo atual
    saldo = 0
    for mov in todas_movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    print(f"\n[INFO] Saldo atual: {saldo} animais")
    
    # Se saldo for negativo, deletar movimentações que causam o problema
    if saldo < 0:
        print(f"\n[PASSO] Deletando movimentacoes incorretas...")
        
        # Deletar todas as movimentações de 2025 que não sejam da transferência de 2022
        movimentacoes_2025 = todas_movimentacoes.filter(data_movimentacao__year=2025)
        
        print(f"[INFO] Movimentacoes em 2025: {movimentacoes_2025.count()}")
        
        # Deletar vendas e transferências de 2025 que causam saldo negativo
        movimentacoes_para_deletar = movimentacoes_2025.filter(
            tipo_movimentacao__in=['VENDA', 'TRANSFERENCIA_SAIDA']
        )
        
        total_deletadas = movimentacoes_para_deletar.count()
        movimentacoes_para_deletar.delete()
        print(f"[OK] {total_deletadas} movimentacoes deletadas")
    
    # Verificar saldo final
    movimentacoes_restantes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    saldo_final = 0
    for mov in movimentacoes_restantes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo_final += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo_final -= mov.quantidade
    
    print(f"\n[VERIFICACAO] Saldo final: {saldo_final} animais")
    
    if saldo_final == 0:
        print("[OK] Saldo zerado com sucesso!")
    else:
        print(f"[AVISO] Saldo ainda nao esta zerado: {saldo_final}")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Processo concluido!")
    print("=" * 80)


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        corrigir_saldo_negativo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










