# -*- coding: utf-8 -*-
"""
Script para garantir configuração padrão da Invernada Grande após nova projeção
Este script DEVE ser executado após cada nova geração de projeção

CONFIGURAÇÃO PADRÃO:
- Sem inventário inicial
- Recebe 512 vacas descarte da Canta Galo em 2022
- Vende 80 cabeças mensais até zerar (fevereiro a agosto de 2022)
- Saldo zerado em 2023, 2024, 2025
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
from decimal import Decimal
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho, VendaProjetada
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


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível considerando inventário e movimentações"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até a data
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)


@transaction.atomic
def garantir_configuracao_invernada_grande():
    """Garante configuração padrão da Invernada Grande"""
    
    print("=" * 80)
    print("GARANTIR CONFIGURACAO PADRAO INVERNADA GRANDE")
    print("=" * 80)
    print("Este script aplica a configuracao padrao apos nova projecao:")
    print("- Sem inventario inicial")
    print("- Recebe 365 vacas descarte da Canta Galo (de um total de 512)")
    print("- Vende 80 cabecas mensais ate zerar")
    print("- Saldo zerado apos todas as vendas")
    print("=" * 80)
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar categoria
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar planejamentos
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_canta or not planejamento_invernada:
        print("[ERRO] Planejamentos nao encontrados")
        return
    
    print(f"\n[INFO] Planejamento Canta Galo: {planejamento_canta.codigo}")
    print(f"[INFO] Planejamento Invernada: {planejamento_invernada.codigo}")
    
    # ========== 1. DELETAR INVENTÁRIO INICIAL ==========
    print("\n[PASSO 1] Deletando inventario inicial...")
    
    inventarios = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte
    )
    
    total_inventarios = inventarios.count()
    if total_inventarios > 0:
        inventarios.delete()
        print(f"[OK] {total_inventarios} inventarios deletados")
    else:
        print("[OK] Nenhum inventario encontrado (ja esta correto)")
    
    # ========== 2. BUSCAR TRANSFERÊNCIAS DE SAÍDA DA CANTA GALO ==========
    print("\n[PASSO 2] Buscando transferencias de saida da Canta Galo...")
    
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_canta
    ).order_by('data_movimentacao')
    
    quantidade_total_disponivel = sum(saida.quantidade for saida in saidas_canta)
    print(f"[INFO] Transferencias encontradas: {saidas_canta.count()}")
    print(f"[INFO] Quantidade total disponivel na Canta Galo: {quantidade_total_disponivel} vacas")
    
    if not saidas_canta.exists():
        print("[AVISO] Nenhuma transferencia de saida encontrada na Canta Galo")
        return
    
    # ========== 3. CRIAR ENTRADAS NA INVERNADA GRANDE (LIMITADO A 365 VACAS) ==========
    print("\n[PASSO 3] Criando entradas na Invernada Grande (limitado a 365 vacas)...")
    
    # Quantidade total a transferir: 365 vacas (não todas as 512)
    quantidade_total_transferir = 365
    quantidade_transferida = 0
    entradas_criadas = 0
    
    for saida in saidas_canta:
        if quantidade_transferida >= quantidade_total_transferir:
            print(f"  [INFO] Limite de 365 vacas atingido. Parando transferencias.")
            break
            
        ano = saida.data_movimentacao.year
        quantidade_saida = saida.quantidade
        data_transferencia = saida.data_movimentacao
        
        # Calcular quantidade a transferir (não pode exceder 365)
        quantidade_restante = quantidade_total_transferir - quantidade_transferida
        quantidade_transferir = min(quantidade_saida, quantidade_restante)
        
        if quantidade_transferir <= 0:
            continue
        
        # Verificar se já existe entrada
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=data_transferencia,
            planejamento=planejamento_invernada
        ).first()
        
        if entrada_existente:
            # Atualizar quantidade se necessário
            if entrada_existente.quantidade != quantidade_transferir:
                entrada_existente.quantidade = quantidade_transferir
                entrada_existente.observacao = f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (de {quantidade_saida} disponiveis, ano {ano}) - CONFIGURACAO PADRAO - LIMITADO A 365'
                entrada_existente.save()
                print(f"  [OK] Entrada atualizada: {quantidade_transferir} vacas em {data_transferencia.strftime('%d/%m/%Y')} (era {entrada_existente.quantidade})")
            else:
                print(f"  [INFO] Entrada ja existe para {data_transferencia.strftime('%d/%m/%Y')} com quantidade correta")
        else:
            # Criar entrada
            MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_invernada,
                observacao=f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (de {quantidade_saida} disponiveis, ano {ano}) - CONFIGURACAO PADRAO - LIMITADO A 365'
            )
            print(f"  [OK] Entrada criada: {quantidade_transferir} vacas em {data_transferencia.strftime('%d/%m/%Y')} (de {quantidade_saida} disponiveis na Canta Galo)")
            entradas_criadas += 1
        
        quantidade_transferida += quantidade_transferir
    
    print(f"\n[RESUMO] Total transferido: {quantidade_transferida} vacas (limite: 365)")
    print(f"[RESUMO] Entradas criadas/atualizadas: {entradas_criadas}")
    
    # ========== 4. DELETAR VENDAS EXISTENTES PARA RECRIAR ==========
    print("\n[PASSO 4] Deletando vendas existentes para recriar...")
    
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        planejamento=planejamento_invernada
    )
    
    total_vendas_deletadas = vendas_existentes.count()
    vendas_existentes.delete()
    
    # Deletar também VendaProjetada relacionadas
    vendas_projetadas = VendaProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        planejamento=planejamento_invernada
    )
    total_vendas_projetadas_deletadas = vendas_projetadas.count()
    vendas_projetadas.delete()
    
    print(f"[OK] {total_vendas_deletadas} movimentacoes de venda deletadas")
    print(f"[OK] {total_vendas_projetadas_deletadas} registros de VendaProjetada deletados")
    
    # ========== 5. CRIAR VENDAS MENSAIS DE 80 CABEÇAS (APENAS PARA AS 365 VACAS) ==========
    print("\n[PASSO 5] Criando vendas mensais de 80 cabecas para as 365 vacas transferidas...")
    
    # Buscar entradas criadas na Invernada Grande
    entradas_invernada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_invernada
    ).order_by('data_movimentacao')
    
    if not entradas_invernada.exists():
        print("[ERRO] Nenhuma entrada encontrada na Invernada Grande. Execute o PASSO 3 primeiro.")
        return
    
    # Calcular quantidade total a vender (soma de todas as entradas, limitado a 365)
    quantidade_total_vender = sum(entrada.quantidade for entrada in entradas_invernada)
    quantidade_total_vender = min(quantidade_total_vender, 365)  # Garantir que não exceda 365
    
    print(f"[INFO] Quantidade total a vender: {quantidade_total_vender} vacas")
    
    vendas_criadas = 0
    
    # Usar a primeira entrada para determinar a data de início
    primeira_entrada = entradas_invernada.first()
    data_transferencia = primeira_entrada.data_movimentacao
    ano = data_transferencia.year
    
    print(f"\n[ANO {ano}] Processando vendas para {quantidade_total_vender} vacas...")
    
    # Primeira venda: 1 mês após a transferência
    data_venda = date(data_transferencia.year, data_transferencia.month + 1, 15)
    if data_venda.month > 12:
        data_venda = date(data_venda.year + 1, 1, 15)
    
    quantidade_restante = quantidade_total_vender
    lote = 1
    
    # Criar vendas mensais de 80 cabeças até zerar
    while quantidade_restante > 0:
            quantidade_venda = min(80, quantidade_restante)
            
            # Verificar saldo disponível antes de criar venda
            saldo_disponivel = calcular_saldo_disponivel(
                invernada, categoria_descarte, data_venda, planejamento_invernada
            )
            
            if saldo_disponivel <= 0:
                print(f"  [AVISO] Sem saldo disponivel em {data_venda.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
                break
            
            # Ajustar quantidade se necessário
            quantidade_venda = min(quantidade_venda, saldo_disponivel)
            
            # Valores
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_venda))
            peso_total = peso_medio_kg * Decimal(str(quantidade_venda))
            
            # Criar movimentação de venda
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_venda,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (ano {ano}) - CONFIGURACAO PADRAO'
            )
            
            # Criar VendaProjetada
            VendaProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                planejamento=planejamento_invernada,
                data_venda=data_venda,
                quantidade=quantidade_venda,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_total,
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (ano {ano}) - CONFIGURACAO PADRAO'
            )
            
            print(f"  [OK] Venda criada: {quantidade_venda} vacas em {data_venda.strftime('%d/%m/%Y')} (saldo antes: {saldo_disponivel}, restante: {quantidade_restante - quantidade_venda})")
            
            quantidade_restante -= quantidade_venda
            lote += 1
            
            # Próximo mês
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 15)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 15)
            
            vendas_criadas += 1
    
    print(f"\n[RESUMO] Vendas criadas: {vendas_criadas}")
    
    # ========== 6. GARANTIR QUE SALDO SEJA ZERADO APÓS TODAS AS VENDAS ==========
    print("\n[PASSO 6] Verificando e garantindo que saldo seja zerado...")
    
    # Calcular saldo final após todas as vendas
    # Buscar última data de venda
    ultima_venda = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        planejamento=planejamento_invernada
    ).order_by('-data_movimentacao').first()
    
    if ultima_venda:
        data_final = ultima_venda.data_movimentacao
        saldo_final = calcular_saldo_disponivel(
            invernada, categoria_descarte, data_final, planejamento_invernada
        )
        
        if saldo_final > 0:
            print(f"  [AVISO] Saldo final ainda nao zerado: {saldo_final} vacas")
            print(f"  [INFO] Criando venda adicional para zerar saldo...")
            
            # Criar venda adicional para zerar
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(saldo_final))
            peso_total = peso_medio_kg * Decimal(str(saldo_final))
            
            # Data: 1 mês após a última venda
            data_venda_final = date(data_final.year, data_final.month + 1, 15)
            if data_venda_final.month > 12:
                data_venda_final = date(data_venda_final.year + 1, 1, 15)
            
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_venda_final,
                tipo_movimentacao='VENDA',
                quantidade=saldo_final,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda final para zerar saldo - {saldo_final} vacas descarte - CONFIGURACAO PADRAO'
            )
            
            VendaProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                planejamento=planejamento_invernada,
                data_venda=data_venda_final,
                quantidade=saldo_final,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_total,
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda_final + timedelta(days=30),
                observacoes=f'Venda final para zerar saldo - {saldo_final} vacas descarte - CONFIGURACAO PADRAO'
            )
            
            print(f"  [OK] Venda final criada: {saldo_final} vacas em {data_venda_final.strftime('%d/%m/%Y')}")
            vendas_criadas += 1
        else:
            print(f"  [OK] Saldo final zerado corretamente")
    else:
        print("  [AVISO] Nenhuma venda encontrada para verificar saldo final")
    
    # ========== 7. DELETAR MOVIMENTAÇÕES DE ANOS FUTUROS (SE HOUVER) ==========
    print("\n[PASSO 7] Deletando movimentacoes incorretas de anos futuros...")
    
    # Buscar ano da última venda ou usar 2023 como limite
    ano_limite = ultima_venda.data_movimentacao.year + 1 if ultima_venda else 2024
    
    movimentacoes_futuras = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao__year__gt=ano_limite,
        planejamento=planejamento_invernada
    )
    
    total_deletadas = movimentacoes_futuras.count()
    if total_deletadas > 0:
        movimentacoes_futuras.delete()
        print(f"[OK] {total_deletadas} movimentacoes futuras deletadas")
    else:
        print("[OK] Nenhuma movimentacao incorreta encontrada")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Configuracao padrao aplicada!")
    print("=" * 80)
    print("\n[RESUMO FINAL]")
    print("  - Inventario inicial: DELETADO")
    print(f"  - Entradas: {quantidade_transferida} vacas (limitado a 365)")
    print(f"  - Vendas: {vendas_criadas} vendas mensais criadas")
    print("  - Saldo: ZERADO apos todas as vendas")
    print("\n[IMPORTANTE] Execute este script apos cada nova geracao de projecao!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        garantir_configuracao_invernada_grande()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

