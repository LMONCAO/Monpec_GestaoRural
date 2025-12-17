# -*- coding: utf-8 -*-
"""
Script para converter transferências de vacas descarte em vendas na Fazenda Canta Galo.
Valor: R$ 3.500,00 por animal
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date
from django.db import transaction
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    VendaProjetada
)


@transaction.atomic
def converter_transferencias_em_vendas():
    """Converte transferências de vacas descarte em vendas na Canta Galo"""
    
    # Buscar fazenda Canta Galo
    canta_galo = Propriedade.objects.filter(nome_propriedade__icontains='CANTA GALO').first()
    if not canta_galo:
        print("[ERRO] Fazenda Canta Galo não encontrada")
        return
    
    print(f"[INFO] Fazenda: {canta_galo.nome_propriedade}")
    
    # Buscar categoria de vacas descarte
    categoria_descarte = CategoriaAnimal.objects.filter(
        nome__icontains='descarte'
    ).first()
    
    if not categoria_descarte:
        print("[ERRO] Categoria 'Vacas Descarte' não encontrada")
        return
    
    print(f"[INFO] Categoria: {categoria_descarte.nome}")
    
    # Buscar todas as transferências de saída de vacas descarte da Canta Galo
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA'
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Encontradas {transferencias_saida.count()} transferências de saída")
    
    if transferencias_saida.count() == 0:
        print("[INFO] Nenhuma transferência encontrada. Nada a fazer.")
        return
    
    # Agrupar por ano e data para criar vendas
    vendas_criadas = 0
    transferencias_deletadas = 0
    
    # Valor por animal
    valor_por_animal = Decimal('3500.00')
    
    # Peso médio padrão para vacas descarte (450 kg)
    peso_medio_kg = Decimal('450.00')
    if categoria_descarte.peso_medio_kg:
        peso_medio_kg = categoria_descarte.peso_medio_kg
    
    # Calcular valor por kg
    valor_por_kg = valor_por_animal / peso_medio_kg if peso_medio_kg > 0 else Decimal('7.78')
    
    for transferencia in transferencias_saida:
        quantidade = transferencia.quantidade
        data_transferencia = transferencia.data_movimentacao
        ano = data_transferencia.year
        
        print(f"\n[ANO {ano}] Processando transferência de {quantidade} vacas em {data_transferencia.strftime('%d/%m/%Y')}")
        
        # Verificar se já existe venda para esta data e quantidade
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao='VENDA',
            data_movimentacao=data_transferencia,
            quantidade=quantidade
        ).first()
        
        if venda_existente:
            print(f"  [INFO] Venda já existe para esta data e quantidade. Pulando...")
            continue
        
        # Buscar transferências de entrada correspondentes em outras fazendas
        transferencias_entrada = MovimentacaoProjetada.objects.filter(
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=data_transferencia,
            quantidade=quantidade,
            observacao__icontains='Canta Galo'
        )
        
        # Deletar transferências de entrada correspondentes
        for entrada in transferencias_entrada:
            print(f"  [DELETANDO] Transferência de entrada em {entrada.propriedade.nome_propriedade}")
            entrada.delete()
            transferencias_deletadas += 1
        
        # Deletar transferência de saída
        print(f"  [DELETANDO] Transferência de saída")
        transferencia.delete()
        transferencias_deletadas += 1
        
        # Criar venda
        peso_total = peso_medio_kg * Decimal(str(quantidade))
        valor_total = valor_por_animal * Decimal(str(quantidade))
        
        # Criar movimentação de venda
        movimentacao_venda = MovimentacaoProjetada.objects.create(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='VENDA',
            quantidade=quantidade,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            observacao=f'Venda de vacas de descarte - {quantidade} cabeças a R$ {valor_por_animal:,.2f} por animal (Total: R$ {valor_total:,.2f}) - Convertido de transferência'
        )
        
        # Criar venda projetada
        VendaProjetada.objects.create(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao_venda,
            data_venda=data_transferencia,
            quantidade=quantidade,
            cliente_nome='Venda de Vacas Descarte',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_total,
            valor_por_kg=valor_por_kg,
            valor_total=valor_total,
            observacao=f'Venda de vacas de descarte convertida de transferência'
        )
        
        print(f"  [OK] Venda criada: {quantidade} vacas a R$ {valor_por_animal:,.2f} por animal (Total: R$ {valor_total:,.2f})")
        vendas_criadas += 1
    
    print(f"\n[RESUMO]")
    print(f"  Transferências deletadas: {transferencias_deletadas}")
    print(f"  Vendas criadas: {vendas_criadas}")
    print(f"\n[OK] Conversão concluída!")


if __name__ == '__main__':
    try:
        converter_transferencias_em_vendas()
    except Exception as e:
        print(f"\n[ERRO] Erro ao converter transferências: {e}")
        import traceback
        traceback.print_exc()










