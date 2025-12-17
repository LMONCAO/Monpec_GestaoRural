# -*- coding: utf-8 -*-
"""
Script para:
1. Baixar 15 machos (Boi 24-36 M) como morte na Girassol em 2023
2. Vender todas as 10 cabeças restantes na Invernada Grande em 2023
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    # Buscar inventário inicial (mais recente, independente da data)
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria
    ).order_by('-data_inventario').first()
    
    saldo = 0
    
    # Se há inventário inicial, considerar como saldo inicial
    if inventario_inicial:
        saldo = inventario_inicial.quantidade
    
    # Aplicar todas as movimentações até a data de referência
    # Se o inventário tem data posterior, considerar todas as movimentações
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
            if saldo < 0:
                saldo = 0
    
    return saldo


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
def corrigir_mortes_e_vendas():
    """Corrige mortes na Girassol e vendas na Invernada Grande"""
    
    print("=" * 80)
    print("CORRIGIR MORTES GIRASSOL E VENDAS INVERNADA GRANDE 2023")
    print("=" * 80)
    
    # ========== 1. MORTES NA GIRASSOL ==========
    print("\n[PASSO 1] Criando mortes de 15 bois na Girassol em 2023...")
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi
    ).order_by('-data_inventario').first()
    
    saldo_inicial = 0
    if inventario_inicial:
        saldo_inicial = inventario_inicial.quantidade
    
    # Verificar saldo disponível em 2023 (incluindo inventário inicial)
    saldo_2023 = calcular_saldo_disponivel(girassol, categoria_boi, date(2023, 12, 31))
    
    print(f"   [INFO] Inventario inicial: {saldo_inicial}")
    print(f"   [INFO] Saldo disponivel de bois em 2023: {saldo_2023}")
    
    # Se o saldo calculado não incluir o inventário inicial, adicionar
    if saldo_inicial > 0 and saldo_2023 < saldo_inicial:
        saldo_2023 = saldo_inicial
    
    if saldo_2023 >= 15:
        # Data da morte: final de 2023
        data_morte = date(2023, 12, 15)
        
        # Verificar se já existe morte registrada
        morte_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='MORTE',
            categoria=categoria_boi,
            data_movimentacao__year=2023,
            quantidade=15
        ).first()
        
        if not morte_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_boi,
                data_movimentacao=data_morte,
                tipo_movimentacao='MORTE',
                quantidade=15,
                planejamento=planejamento_girassol,
                observacao='Morte de 15 bois machos em 2023'
            )
            print(f"   [OK] Morte criada: 15 bois em {data_morte.strftime('%d/%m/%Y')}")
        else:
            print(f"   [INFO] Morte ja existe")
    else:
        quantidade_morte = min(15, saldo_2023)
        if quantidade_morte > 0:
            data_morte = date(2023, 12, 15)
            
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_boi,
                data_movimentacao=data_morte,
                tipo_movimentacao='MORTE',
                quantidade=quantidade_morte,
                planejamento=planejamento_girassol,
                observacao=f'Morte de {quantidade_morte} bois machos em 2023'
            )
            print(f"   [OK] Morte criada: {quantidade_morte} bois em {data_morte.strftime('%d/%m/%Y')}")
        else:
            print(f"   [AVISO] Sem saldo disponivel para criar morte")
    
    # ========== 2. VENDAS NA INVERNADA GRANDE ==========
    print("\n[PASSO 2] Criando vendas das 10 cabeças restantes na Invernada Grande em 2023...")
    
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=invernada_grande,
        categoria=categoria_descarte
    ).order_by('-data_inventario').first()
    
    saldo_inicial = 0
    if inventario_inicial:
        saldo_inicial = inventario_inicial.quantidade
    
    # Verificar saldo disponível em 2023 (incluindo inventário inicial)
    saldo_invernada_2023 = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"   [INFO] Inventario inicial: {saldo_inicial}")
    print(f"   [INFO] Saldo disponivel de vacas descarte em 2023: {saldo_invernada_2023}")
    
    # Se o saldo calculado não incluir o inventário inicial, adicionar
    if saldo_inicial > 0 and saldo_invernada_2023 < saldo_inicial:
        saldo_invernada_2023 = saldo_inicial
    
    if saldo_invernada_2023 > 0:
        # Data da venda: final de 2023
        data_venda = date(2023, 12, 20)
        
        # Verificar se já existe venda para essa quantidade nesta data
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada_grande,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            quantidade=saldo_invernada_2023
        ).first()
        
        if not venda_existente:
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(saldo_invernada_2023))
            
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=saldo_invernada_2023,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda final para zerar saldo 2023 - {saldo_invernada_2023} vacas descarte'
            )
            
            VendaProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                data_venda=data_venda,
                quantidade=saldo_invernada_2023,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_medio_kg * Decimal(str(saldo_invernada_2023)),
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda final para zerar saldo 2023'
            )
            
            print(f"   [OK] Venda criada: {saldo_invernada_2023} vacas em {data_venda.strftime('%d/%m/%Y')} - R$ {valor_total:.2f}")
        else:
            print(f"   [INFO] Venda ja existe")
    else:
        print(f"   [INFO] Saldo ja esta zerado")
    
    # Verificar saldos finais
    print("\n[PASSO 3] Verificando saldos finais...")
    
    saldo_final_girassol = calcular_saldo_disponivel(girassol, categoria_boi, date(2023, 12, 31))
    saldo_final_invernada = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"   [INFO] Saldo final Girassol (Boi 24-36 M): {saldo_final_girassol}")
    print(f"   [INFO] Saldo final Invernada Grande (Vacas Descarte): {saldo_final_invernada}")
    
    if saldo_final_girassol == 0:
        print(f"   [OK] Saldo da Girassol zerado!")
    else:
        print(f"   [AVISO] Ainda ha {saldo_final_girassol} bois na Girassol")
    
    if saldo_final_invernada == 0:
        print(f"   [OK] Saldo da Invernada Grande zerado!")
    else:
        print(f"   [AVISO] Ainda ha {saldo_final_invernada} vacas na Invernada Grande")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_mortes_e_vendas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

