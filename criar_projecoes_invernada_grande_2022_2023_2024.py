# -*- coding: utf-8 -*-
"""
Script para criar projeções para 2022, 2023 e 2024 na Invernada Grande
e corrigir saldo negativo vendendo as vacas restantes
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from decimal import Decimal
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        saldo = inventario_inicial.quantidade
    
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        **filtro_data
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
def criar_projecoes_e_corrigir_saldo():
    """Cria projeções para 2022-2024 e corrige saldo negativo"""
    
    print("=" * 80)
    print("CRIAR PROJECOES INVERNADA GRANDE 2022-2024 E CORRIGIR SALDO")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento: {planejamento.codigo}")
    
    # Verificar transferências existentes
    transferencias_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de entrada encontradas: {transferencias_entrada.count()}")
    
    # Criar vendas para cada transferência (80 cabeças por mês até acabar)
    for transferencia in transferencias_entrada:
        ano = transferencia.data_movimentacao.year
        quantidade_total = transferencia.quantidade
        data_inicio = transferencia.data_movimentacao
        
        print(f"\n[ANO {ano}] Transferencia de {quantidade_total} vacas em {data_inicio.strftime('%d/%m/%Y')}")
        
        # Verificar se já existem vendas para este ano
        vendas_existentes = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao__year=ano
        )
        
        total_vendido = sum(v.quantidade for v in vendas_existentes)
        
        if total_vendido >= quantidade_total:
            print(f"  [INFO] Vendas ja existem: {total_vendido} vendidas")
            continue
        
        # Criar vendas mensais de 80 cabeças
        quantidade_restante = quantidade_total - total_vendido
        data_venda = date(ano, data_inicio.month + 1, 15)  # Primeira venda 1 mês após entrada
        
        lote = 1
        while quantidade_restante > 0:
            quantidade_venda = min(80, quantidade_restante)
            
            # Verificar se já existe venda nesta data
            venda_existente = MovimentacaoProjetada.objects.filter(
                propriedade=invernada,
                tipo_movimentacao='VENDA',
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                quantidade=quantidade_venda
            ).first()
            
            if not venda_existente:
                # Verificar saldo disponível
                saldo_disponivel = calcular_saldo_disponivel(invernada, categoria_descarte, data_venda)
                
                if saldo_disponivel >= quantidade_venda:
                    # Criar movimentação de venda
                    movimentacao = MovimentacaoProjetada.objects.create(
                        propriedade=invernada,
                        categoria=categoria_descarte,
                        data_movimentacao=data_venda,
                        tipo_movimentacao='VENDA',
                        quantidade=quantidade_venda,
                        planejamento=planejamento,
                        observacao=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                    )
                    
                    # Criar venda projetada
                    valor_por_kg = Decimal('7.00')
                    peso_medio_kg = Decimal('440.00')
                    valor_por_animal = valor_por_kg * peso_medio_kg
                    valor_total = valor_por_animal * Decimal(str(quantidade_venda))
                    
                    VendaProjetada.objects.create(
                        propriedade=invernada,
                        categoria=categoria_descarte,
                        movimentacao_projetada=movimentacao,
                        data_venda=data_venda,
                        quantidade=quantidade_venda,
                        cliente_nome='JBS',
                        peso_medio_kg=peso_medio_kg,
                        peso_total_kg=peso_medio_kg * Decimal(str(quantidade_venda)),
                        valor_por_kg=valor_por_kg,
                        valor_por_animal=valor_por_animal,
                        valor_total=valor_total,
                        data_recebimento=data_venda,
                        observacoes=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                    )
                    
                    print(f"  [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
                else:
                    print(f"  [AVISO] Saldo insuficiente em {data_venda.strftime('%d/%m/%Y')}: {saldo_disponivel} < {quantidade_venda}")
                    quantidade_venda = saldo_disponivel
                    if quantidade_venda > 0:
                        # Criar venda com saldo disponível
                        movimentacao = MovimentacaoProjetada.objects.create(
                            propriedade=invernada,
                            categoria=categoria_descarte,
                            data_movimentacao=data_venda,
                            tipo_movimentacao='VENDA',
                            quantidade=quantidade_venda,
                            planejamento=planejamento,
                            observacao=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                        )
                        
                        valor_por_kg = Decimal('7.00')
                        peso_medio_kg = Decimal('440.00')
                        valor_por_animal = valor_por_kg * peso_medio_kg
                        valor_total = valor_por_animal * Decimal(str(quantidade_venda))
                        
                        VendaProjetada.objects.create(
                            propriedade=invernada,
                            categoria=categoria_descarte,
                            movimentacao_projetada=movimentacao,
                            data_venda=data_venda,
                            quantidade=quantidade_venda,
                            cliente_nome='JBS',
                            peso_medio_kg=peso_medio_kg,
                            peso_total_kg=peso_medio_kg * Decimal(str(quantidade_venda)),
                            valor_por_kg=valor_por_kg,
                            valor_por_animal=valor_por_animal,
                            valor_total=valor_total,
                            data_recebimento=data_venda,
                            observacoes=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                        )
                        print(f"  [OK] Venda criada com saldo disponivel: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
            
            quantidade_restante -= quantidade_venda
            
            # Próxima venda: próximo mês
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 15)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 15)
            
            lote += 1
            
            # Limite de segurança
            if lote > 20:
                break
    
    # Corrigir saldo negativo de 2025 vendendo as 2 vacas restantes
    print(f"\n[CORRIGIR SALDO NEGATIVO 2025]")
    saldo_2025 = calcular_saldo_disponivel(invernada, categoria_descarte, date(2025, 12, 31))
    
    if saldo_2025 < 0:
        quantidade_vender = abs(saldo_2025)
        print(f"  [INFO] Saldo negativo: {saldo_2025}, vendendo {quantidade_vender} vacas")
        
        # Criar venda para zerar o saldo
        data_venda = date(2025, 12, 30)
        
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            quantidade=quantidade_vender
        ).first()
        
        if not venda_existente:
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_vender,
                planejamento=planejamento,
                observacao=f'Venda para zerar saldo negativo - {quantidade_vender} vacas descarte (ano 2025)'
            )
            
            valor_por_kg = Decimal('7.00')
            peso_medio_kg = Decimal('440.00')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_vender))
            
            VendaProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                data_venda=data_venda,
                quantidade=quantidade_vender,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_medio_kg * Decimal(str(quantidade_vender)),
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda,
                observacoes=f'Venda para zerar saldo negativo - {quantidade_vender} vacas descarte (ano 2025)'
            )
            
            print(f"  [OK] Venda criada: {quantidade_vender} vacas em {data_venda.strftime('%d/%m/%Y')}")
        else:
            print(f"  [INFO] Venda ja existe")
    else:
        print(f"  [INFO] Saldo positivo: {saldo_2025}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_projecoes_e_corrigir_saldo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























