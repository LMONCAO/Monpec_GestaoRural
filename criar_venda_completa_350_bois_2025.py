# -*- coding: utf-8 -*-
"""
Script para criar venda completa de 350 bois em 30/12/2025
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada
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
def criar_venda_completa():
    """Cria venda completa de 350 bois em 30/12/2025"""
    
    print("=" * 80)
    print("CRIAR VENDA COMPLETA 350 BOIS - 30/12/2025")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    data_venda = date(2025, 12, 30)
    quantidade = 350
    
    # Verificar se já existe venda nesta data
    venda_existente = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao=data_venda,
        planejamento=planejamento
    ).first()
    
    if venda_existente:
        # Atualizar quantidade
        quantidade_atual = venda_existente.quantidade
        venda_existente.quantidade = quantidade
        venda_existente.save()
        
        # Atualizar VendaProjetada
        venda_proj = VendaProjetada.objects.filter(movimentacao_projetada=venda_existente).first()
        if venda_proj:
            venda_proj.quantidade = quantidade
            venda_proj.valor_total = venda_proj.valor_por_animal * Decimal(str(quantidade))
            venda_proj.peso_total_kg = venda_proj.peso_medio_kg * Decimal(str(quantidade))
            venda_proj.save()
        
        print(f"[OK] Venda atualizada: {quantidade_atual} -> {quantidade} bois")
    else:
        # Criar nova venda
        valor_por_kg = Decimal('7.00')
        peso_medio_kg = Decimal('500.00')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(quantidade))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_boi,
            data_movimentacao=data_venda,
            tipo_movimentacao='VENDA',
            quantidade=quantidade,
            planejamento=planejamento,
            observacao=f'Venda completa do lote - {quantidade} bois apos 90 dias da evolucao (evolucao em 01/10/2025)'
        )
        
        VendaProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_boi,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda,
            quantidade=quantidade,
            cliente_nome='Frigorifico',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(quantidade)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda + timedelta(days=30),
            observacoes=f'Venda completa do lote - {quantidade} bois apos 90 dias da evolucao (evolucao em 01/10/2025)'
        )
        
        print(f"[OK] Venda criada: {quantidade} bois em {data_venda.strftime('%d/%m/%Y')}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_venda_completa()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











