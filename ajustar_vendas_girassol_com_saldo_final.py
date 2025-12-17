# -*- coding: utf-8 -*-
"""
Script para ajustar vendas da Girassol para que sobre quantidade específica no final de cada ano
2022: 300 animais
2023: 250 animais
2024: 400 animais
2025: 320 animais
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


def calcular_saldo_final_ano(propriedade, categoria, ano):
    """Calcula o saldo final de um ano"""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=date(ano, 12, 31)
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
        data_movimentacao__year=ano,
        **filtro_data
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
    
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
def ajustar_vendas_com_saldo_final():
    """Ajusta vendas para que sobre quantidade específica no final de cada ano"""
    
    print("=" * 80)
    print("AJUSTAR VENDAS GIRASSOL COM SALDO FINAL ESPECIFICO")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento: {planejamento.codigo}")
    
    # Saldos finais desejados por ano
    saldos_finais_desejados = {
        2022: 300,
        2023: 250,
        2024: 400,
        2025: 320
    }
    
    for ano, saldo_desejado in saldos_finais_desejados.items():
        print(f"\n[ANO {ano}] Saldo final desejado: {saldo_desejado} bois")
        
        # Calcular saldo atual sem vendas do ano
        # Buscar inventário inicial (pode ser de ano anterior)
        inventario_inicial = InventarioRebanho.objects.filter(
            propriedade=girassol,
            categoria=categoria_boi,
            data_inventario__lte=date(ano, 12, 31)
        ).order_by('-data_inventario').first()
        
        saldo_sem_vendas = inventario_inicial.quantidade if inventario_inicial else 0
        
        # Se não há inventário, considerar saldo final do ano anterior
        if not inventario_inicial or inventario_inicial.data_inventario.year < ano:
            # Calcular saldo final do ano anterior
            if ano > 2022:
                saldo_ano_anterior = calcular_saldo_final_ano(girassol, categoria_boi, ano - 1)
                saldo_sem_vendas = saldo_ano_anterior
                print(f"  [INFO] Usando saldo final do ano anterior ({ano-1}): {saldo_ano_anterior}")
        
        # Adicionar evoluções do ano (considerando movimentações até o final do ano)
        evolucoes_ano = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            categoria=categoria_boi,
            data_movimentacao__year=ano,
            data_movimentacao__lte=date(ano, 12, 31),
            planejamento=planejamento
        )
        
        total_evolucoes = sum(e.quantidade for e in evolucoes_ano)
        saldo_sem_vendas += total_evolucoes
        
        # Subtrair mortes do ano (mas não vendas ainda)
        mortes_ano = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='MORTE',
            categoria=categoria_boi,
            data_movimentacao__year=ano,
            data_movimentacao__lte=date(ano, 12, 31),
            planejamento=planejamento
        )
        
        total_mortes = sum(m.quantidade for m in mortes_ano)
        saldo_sem_vendas -= total_mortes
        
        print(f"  [INFO] Saldo sem vendas: {saldo_sem_vendas} (inicial: {inventario_inicial.quantidade if inventario_inicial else 0}, evolucoes: {total_evolucoes}, mortes: {total_mortes})")
        
        # Calcular quanto deve ser vendido
        quantidade_a_vender = saldo_sem_vendas - saldo_desejado
        
        if quantidade_a_vender <= 0:
            print(f"  [AVISO] Nao precisa vender (saldo ja e menor ou igual ao desejado)")
            continue
        
        print(f"  [INFO] Quantidade a vender: {quantidade_a_vender}")
        
        # Buscar vendas existentes do ano
        vendas_ano = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='VENDA',
            categoria=categoria_boi,
            data_movimentacao__year=ano,
            planejamento=planejamento
        ).order_by('data_movimentacao')
        
        total_vendido_atual = sum(v.quantidade for v in vendas_ano)
        
        print(f"  [INFO] Total vendido atual: {total_vendido_atual}")
        
        diferenca = quantidade_a_vender - total_vendido_atual
        
        if abs(diferenca) < 1:  # Já está correto
            print(f"  [OK] Vendas ja estao corretas")
            continue
        
        if diferenca > 0:
            # Precisa vender mais
            print(f"  [INFO] Precisa vender mais {diferenca} bois")
            
            # Ajustar a última venda do ano ou criar nova
            if vendas_ano.exists():
                ultima_venda = vendas_ano.last()
                # Aumentar quantidade da última venda
                nova_quantidade = ultima_venda.quantidade + diferenca
                ultima_venda.quantidade = nova_quantidade
                ultima_venda.save()
                
                # Atualizar VendaProjetada
                venda_proj = VendaProjetada.objects.filter(movimentacao_projetada=ultima_venda).first()
                if venda_proj:
                    venda_proj.quantidade = nova_quantidade
                    venda_proj.valor_total = venda_proj.valor_por_animal * Decimal(str(nova_quantidade))
                    venda_proj.peso_total_kg = venda_proj.peso_medio_kg * Decimal(str(nova_quantidade))
                    venda_proj.save()
                
                print(f"  [OK] Ultima venda atualizada: {ultima_venda.quantidade} bois")
            else:
                # Criar nova venda no final do ano
                data_venda = date(ano, 12, 30)
                
                valor_por_kg = Decimal('7.00')
                peso_medio_kg = Decimal('500.00')
                valor_por_animal = valor_por_kg * peso_medio_kg
                valor_total = valor_por_animal * Decimal(str(diferenca))
                
                movimentacao = MovimentacaoProjetada.objects.create(
                    propriedade=girassol,
                    categoria=categoria_boi,
                    data_movimentacao=data_venda,
                    tipo_movimentacao='VENDA',
                    quantidade=diferenca,
                    planejamento=planejamento,
                    observacao=f'Venda ajustada para saldo final de {saldo_desejado} bois (ano {ano})'
                )
                
                from datetime import timedelta
                VendaProjetada.objects.create(
                    propriedade=girassol,
                    categoria=categoria_boi,
                    movimentacao_projetada=movimentacao,
                    data_venda=data_venda,
                    quantidade=diferenca,
                    cliente_nome='Frigorifico',
                    peso_medio_kg=peso_medio_kg,
                    peso_total_kg=peso_medio_kg * Decimal(str(diferenca)),
                    valor_por_kg=valor_por_kg,
                    valor_por_animal=valor_por_animal,
                    valor_total=valor_total,
                    data_recebimento=data_venda + timedelta(days=30),
                    observacoes=f'Venda ajustada para saldo final de {saldo_desejado} bois (ano {ano})'
                )
                
                print(f"  [OK] Nova venda criada: {diferenca} bois em {data_venda.strftime('%d/%m/%Y')}")
        
        elif diferenca < 0:
            # Precisa vender menos (reduzir vendas)
            print(f"  [INFO] Precisa reduzir vendas em {abs(diferenca)} bois")
            
            # Reduzir da última venda
            if vendas_ano.exists():
                ultima_venda = vendas_ano.last()
                nova_quantidade = max(0, ultima_venda.quantidade + diferenca)  # diferenca é negativo
                
                if nova_quantidade > 0:
                    ultima_venda.quantidade = nova_quantidade
                    ultima_venda.save()
                    
                    # Atualizar VendaProjetada
                    venda_proj = VendaProjetada.objects.filter(movimentacao_projetada=ultima_venda).first()
                    if venda_proj:
                        venda_proj.quantidade = nova_quantidade
                        venda_proj.valor_total = venda_proj.valor_por_animal * Decimal(str(nova_quantidade))
                        venda_proj.peso_total_kg = venda_proj.peso_medio_kg * Decimal(str(nova_quantidade))
                        venda_proj.save()
                    
                    print(f"  [OK] Ultima venda reduzida: {ultima_venda.quantidade} bois")
                else:
                    # Deletar venda se quantidade ficou zero
                    VendaProjetada.objects.filter(movimentacao_projetada=ultima_venda).delete()
                    ultima_venda.delete()
                    print(f"  [OK] Ultima venda deletada (quantidade zerada)")
        
        # Verificar saldo final após ajuste
        saldo_final = calcular_saldo_final_ano(girassol, categoria_boi, ano)
        print(f"  [VERIFICACAO] Saldo final apos ajuste: {saldo_final} (desejado: {saldo_desejado})")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        ajustar_vendas_com_saldo_final()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

