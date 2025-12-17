# -*- coding: utf-8 -*-
"""
Script para zerar o saldo da Invernada Grande em 2025 e remover inventário inicial
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
    PlanejamentoAnual, InventarioRebanho
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
def zerar_saldo_invernada_2025():
    """Zera o saldo da Invernada Grande em 2025"""
    
    print("=" * 80)
    print("ZERAR SALDO INVERNADA GRANDE - 2025")
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
    
    # ========== 1. DELETAR INVENTÁRIO INICIAL ==========
    print("\n[PASSO 1] Deletando inventario inicial...")
    
    inventarios = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte
    )
    
    total_inventarios = inventarios.count()
    inventarios.delete()
    print(f"[OK] {total_inventarios} inventarios deletados")
    
    # ========== 2. VERIFICAR SALDO EM 2025 ==========
    print("\n[PASSO 2] Verificando saldo em 2025...")
    
    # Calcular saldo em 31/12/2025
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao__lte=date(2025, 12, 31),
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    saldo = 0
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    print(f"[INFO] Saldo em 31/12/2025: {saldo} animais")
    
    # ========== 3. CRIAR VENDA PARA ZERAR SE NECESSÁRIO ==========
    if saldo > 0:
        print(f"\n[PASSO 3] Criando venda para zerar saldo...")
        
        from decimal import Decimal
        from datetime import timedelta
        from gestao_rural.models import VendaProjetada
        
        data_venda = date(2025, 12, 30)
        
        # Valores
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(saldo))
        peso_total = peso_medio_kg * Decimal(str(saldo))
        
        # Criar movimentação de venda
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada,
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            tipo_movimentacao='VENDA',
            quantidade=saldo,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento,
            observacao=f'Venda final para zerar saldo - {saldo} vacas descarte (fim de 2025)'
        )
        
        # Criar VendaProjetada
        VendaProjetada.objects.create(
            propriedade=invernada,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            planejamento=planejamento,
            data_venda=data_venda,
            quantidade=saldo,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_total,
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda + timedelta(days=30),
            observacoes=f'Venda final para zerar saldo - {saldo} vacas descarte (fim de 2025)'
        )
        
        print(f"[OK] Venda criada: {saldo} animais em {data_venda.strftime('%d/%m/%Y')}")
    else:
        print(f"\n[OK] Saldo ja esta zerado ou negativo")
    
    # ========== 4. VERIFICAR SALDO FINAL ==========
    print(f"\n[PASSO 4] Verificando saldo final...")
    
    movimentacoes_final = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao__lte=date(2026, 1, 1),
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    saldo_final = 0
    for mov in movimentacoes_final:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo_final += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo_final -= mov.quantidade
    
    print(f"[VERIFICACAO] Saldo em 01/01/2026: {saldo_final} animais")
    
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
        zerar_saldo_invernada_2025()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










