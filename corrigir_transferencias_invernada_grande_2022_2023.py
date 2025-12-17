# -*- coding: utf-8 -*-
"""
Script para corrigir transferências de vacas descarte para Invernada Grande:
1. Apenas anos 2022 e 2023 (outros anos não têm arrendamento)
2. Verificar saldo disponível na Canta Galo antes de transferir
3. Em 2023, zerar o saldo da Invernada Grande (todas as vacas vendidas)
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
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario,
            categoria=categoria
        )
        saldo = sum(inv.quantidade for inv in inventarios)
    
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
def corrigir_transferencias_invernada_grande():
    """Corrige transferências de vacas descarte para Invernada Grande"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIAS INVERNADA GRANDE (2022-2023)")
    print("=" * 80)
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar planejamentos
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[OK] Planejamento Canta Galo: {planejamento_canta.codigo}")
    print(f"[OK] Planejamento Invernada Grande: {planejamento_invernada.codigo}")
    
    # ========== 1. DELETAR TRANSFERÊNCIAS DE 2024, 2025, 2026 ==========
    print("\n[PASSO 1] Deletando transferencias de 2024, 2025, 2026...")
    
    # Deletar saídas da Canta Galo
    saidas_apagar = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar entradas na Invernada Grande
    entradas_apagar = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    # Deletar vendas da Invernada Grande desses anos
    vendas_apagar = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2024, 2025, 2026]
    )
    
    total_apagado = saidas_apagar.count() + entradas_apagar.count() + vendas_apagar.count()
    
    # Deletar vendas projetadas associadas
    from gestao_rural.models import VendaProjetada
    vendas_projetadas_apagar = VendaProjetada.objects.filter(
        movimentacao_projetada__in=vendas_apagar
    )
    vendas_projetadas_apagar.delete()
    
    vendas_apagar.delete()
    entradas_apagar.delete()
    saidas_apagar.delete()
    
    print(f"   [OK] {total_apagado} movimentacoes deletadas")
    
    # ========== 2. CORRIGIR TRANSFERÊNCIAS DE 2022 E 2023 ==========
    print("\n[PASSO 2] Corrigindo transferencias de 2022 e 2023...")
    
    # Deletar transferências existentes de 2022 e 2023 para recriar corretamente
    saidas_2022_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2022, 2023]
    )
    
    entradas_2022_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2022, 2023]
    )
    
    entradas_2022_2023.delete()
    saidas_2022_2023.delete()
    
    # Criar transferências corretas para 2022 e 2023
    anos = [2022, 2023]
    transferencias_criadas = 0
    
    for ano in anos:
        # Para 2023, verificar se há promoções durante o ano que criam vacas descarte
        if ano == 2023:
            # Verificar promoções de vacas em reprodução para descarte em 2023
            categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
            promocoes_2023 = MovimentacaoProjetada.objects.filter(
                propriedade=canta_galo,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                categoria=categoria_descarte,
                data_movimentacao__year=2023
            ).order_by('data_movimentacao')
            
            if promocoes_2023.exists():
                # Usar a primeira promoção como data de transferência
                primeira_promocao = promocoes_2023.first()
                data_transferencia = primeira_promocao.data_movimentacao
                quantidade_promovida = sum(p.quantidade for p in promocoes_2023)
                
                # Verificar saldo disponível na data da promoção
                saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
                saldo_disponivel += quantidade_promovida  # Incluir as promoções
                
                quantidade_transferir = min(512, saldo_disponivel)
                
                print(f"   [INFO] Encontradas promocoes em 2023: {quantidade_promovida} vacas descarte")
            else:
                # Se não houver promoções, verificar saldo em 15/01/2023
                data_transferencia = date(ano, 1, 15)
                saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
                
                if saldo_disponivel <= 0:
                    print(f"   [AVISO] Sem saldo disponivel na Canta Galo em {data_transferencia.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
                    continue
                
                quantidade_transferir = min(512, saldo_disponivel)
        else:
            # Para 2022, usar data padrão
            data_transferencia = date(ano, 1, 15)
            
            # Verificar saldo disponível na Canta Galo
            saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
            
            if saldo_disponivel <= 0:
                print(f"   [AVISO] Sem saldo disponivel na Canta Galo em {data_transferencia.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
                continue
            
            # Quantidade a transferir: usar o saldo disponível (ou 512 se houver)
            quantidade_transferir = min(512, saldo_disponivel)
        
        # Criar transferência de saída da Canta Galo
        MovimentacaoProjetada.objects.create(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_canta,
            observacao=f'Transferencia para Invernada Grande - {quantidade_transferir} vacas descarte (ano {ano})'
        )
        
        # Criar transferência de entrada na Invernada Grande
        MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_invernada,
            observacao=f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (ano {ano})'
        )
        
        print(f"   [OK] Transferencia criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')} (saldo disponivel: {saldo_disponivel})")
        transferencias_criadas += 1
    
    # ========== 3. CORRIGIR VENDAS NA INVERNADA GRANDE ==========
    print("\n[PASSO 3] Corrigindo vendas na Invernada Grande...")
    
    # Deletar todas as vendas existentes para recriar corretamente
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte
    )
    
    vendas_projetadas_existentes = VendaProjetada.objects.filter(
        movimentacao_projetada__in=vendas_existentes
    )
    vendas_projetadas_existentes.delete()
    vendas_existentes.delete()
    
    # Buscar entradas na Invernada Grande
    entradas_invernada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year__in=[2022, 2023]
    ).order_by('data_movimentacao')
    
    vendas_criadas = 0
    
    for entrada in entradas_invernada:
        data_entrada = entrada.data_movimentacao
        quantidade_total = entrada.quantidade
        
        # Primeira venda: 1 mês após a entrada
        data_primeira_venda = date(data_entrada.year, data_entrada.month + 1, 1)
        if data_primeira_venda.month > 12:
            data_primeira_venda = date(data_primeira_venda.year + 1, 1, 1)
        
        # Criar vendas mensais de 80 cabeças até acabar
        quantidade_restante = quantidade_total
        data_venda = data_primeira_venda
        lote = 1
        
        while quantidade_restante > 0 and lote <= 10:
            quantidade_venda = min(80, quantidade_restante)
            
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_venda))
            
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_venda,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (entrada em {data_entrada.strftime("%d/%m/%Y")})'
            )
            
            VendaProjetada.objects.create(
                propriedade=invernada_grande,
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
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS'
            )
            
            print(f"   [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
            vendas_criadas += 1
            
            quantidade_restante -= quantidade_venda
            lote += 1
            
            # Próxima venda: 1 mês depois
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 1)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 1)
    
    # ========== 4. VERIFICAR SE 2023 FOI ZERADO ==========
    print("\n[PASSO 4] Verificando se 2023 foi zerado...")
    
    saldo_final_2023 = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    if saldo_final_2023 > 0:
        print(f"   [AVISO] Saldo final de 2023: {saldo_final_2023} (deve ser 0)")
        print(f"   Criando vendas adicionais para zerar...")
        
        # Criar vendas adicionais até zerar
        data_venda = date(2023, 9, 1)  # Começar em setembro/2023
        quantidade_restante = saldo_final_2023
        
        while quantidade_restante > 0 and data_venda.year == 2023:
            quantidade_venda = min(80, quantidade_restante)
            
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_venda))
            
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_venda,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda para zerar saldo 2023 - {quantidade_venda} vacas descarte'
            )
            
            VendaProjetada.objects.create(
                propriedade=invernada_grande,
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
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda para zerar saldo 2023'
            )
            
            print(f"   [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
            quantidade_restante -= quantidade_venda
            
            # Próxima venda: 1 mês depois
            if data_venda.month == 12:
                break
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 1)
    else:
        print(f"   [OK] Saldo final de 2023: {saldo_final_2023} (zerado)")
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas: {transferencias_criadas}")
    print(f"   Vendas criadas: {vendas_criadas}")


if __name__ == '__main__':
    print("\nEste script ira:")
    print("1. Deletar transferencias de 2024, 2025, 2026")
    print("2. Corrigir transferencias de 2022 e 2023 (verificando saldo na Canta Galo)")
    print("3. Criar vendas mensais na Invernada Grande")
    print("4. Garantir que 2023 seja zerado")
    print("\n" + "=" * 80 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias_invernada_grande()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

