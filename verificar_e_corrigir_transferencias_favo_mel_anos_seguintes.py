# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir transferências da Canta Galo para Favo de Mel nos anos seguintes.
A transferência de 1180 garrotes em 2022 foi feita, mas não há transferências nos anos seguintes.
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
from calendar import monthrange
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal
)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    while mes > 12:
        mes -= 12
        ano += 1
    
    ultimo_dia_mes = monthrange(ano, mes)[1]
    if dia > ultimo_dia_mes:
        dia = ultimo_dia_mes
    
    return date(ano, mes, dia)


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
def verificar_e_corrigir_transferencias_favo_mel():
    """Verifica e corrige transferências da Canta Galo para Favo de Mel"""
    
    print("=" * 60)
    print("VERIFICAR E CORRIGIR TRANSFERENCIAS FAVO DE MEL")
    print("=" * 60)
    
    # Buscar propriedades
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        print(f"\n[OK] Propriedade encontrada: {canta_galo.nome_propriedade}")
        print(f"[OK] Propriedade encontrada: {favo_mel.nome_propriedade}")
    except:
        print("[ERRO] Propriedades nao encontradas")
        return
    
    # Buscar categoria garrote
    try:
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    except:
        categoria_garrote = CategoriaAnimal.objects.filter(nome__icontains='Garrote').first()
        if not categoria_garrote:
            print("[ERRO] Categoria 'Garrote' nao encontrada")
            return
    
    print(f"[OK] Categoria encontrada: {categoria_garrote.nome}")
    
    # Buscar planejamento do Favo de Mel
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_favo:
        print("[AVISO] Nenhum planejamento encontrado para Favo de Mel")
    else:
        print(f"[OK] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    
    # Verificar transferências existentes
    transferencias_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de ENTRADA encontradas no Favo de Mel:")
    anos_com_transferencia = set()
    for t in transferencias_entrada:
        ano = t.data_movimentacao.year
        anos_com_transferencia.add(ano)
        print(f"   + {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome} (ano {ano})")
    
    # Verificar transferências de saída da Canta Galo
    transferencias_saida_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        observacao__icontains='Favo de Mel'
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de SAIDA da Canta Galo para Favo de Mel:")
    for t in transferencias_saida_canta:
        print(f"   - {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome} (ano {t.data_movimentacao.year})")
    
    # Verificar quais anos precisam de transferências
    # Assumindo que deve haver transferências anuais a partir de 2022
    anos_necessarios = [2022, 2023, 2024, 2025, 2026]
    anos_faltando = [ano for ano in anos_necessarios if ano not in anos_com_transferencia]
    
    if anos_faltando:
        print(f"\n[INFO] Anos faltando transferencias: {anos_faltando}")
        
        # Buscar planejamento da Canta Galo
        planejamento_canta = PlanejamentoAnual.objects.filter(
            propriedade=canta_galo
        ).order_by('-data_criacao', '-ano').first()
        
        if not planejamento_canta:
            print("[AVISO] Nenhum planejamento encontrado para Canta Galo")
            return
        
        print(f"[OK] Planejamento Canta Galo: {planejamento_canta.codigo}")
        
        # Criar transferências para os anos faltantes
        # Assumindo que a quantidade é similar à de 2022 (1180) ou baseada em alguma lógica
        quantidade_base = 1180  # Quantidade de 2022
        
        transferencias_criadas = 0
        
        for ano in anos_faltando:
            # Data da transferência: 15 de janeiro de cada ano
            data_transferencia = date(ano, 1, 15)
            
            # Verificar se já existe transferência de saída da Canta Galo para este ano
            saida_existente = MovimentacaoProjetada.objects.filter(
                propriedade=canta_galo,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia
            ).first()
            
            if saida_existente:
                quantidade = saida_existente.quantidade
                print(f"\n[INFO] Usando quantidade da transferencia existente: {quantidade}")
            else:
                # Usar quantidade base ou calcular baseado em alguma lógica
                quantidade = quantidade_base
                print(f"\n[INFO] Usando quantidade base: {quantidade}")
            
            # Criar transferência de saída da Canta Galo
            if not saida_existente:
                MovimentacaoProjetada.objects.create(
                    propriedade=canta_galo,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    quantidade=quantidade,
                    planejamento=planejamento_canta,
                    observacao=f'Transferencia para Favo de Mel - {quantidade} garrotes (ano {ano})'
                )
                print(f"   [OK] Transferencia SAIDA criada: {quantidade} em {data_transferencia.strftime('%d/%m/%Y')}")
            
            # Criar transferência de entrada no Favo de Mel
            entrada_existente = MovimentacaoProjetada.objects.filter(
                propriedade=favo_mel,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia
            ).first()
            
            if not entrada_existente:
                MovimentacaoProjetada.objects.create(
                    propriedade=favo_mel,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    quantidade=quantidade,
                    planejamento=planejamento_favo,
                    observacao=f'Transferencia de Canta Galo - {quantidade} garrotes (ano {ano})'
                )
                print(f"   [OK] Transferencia ENTRADA criada: {quantidade} em {data_transferencia.strftime('%d/%m/%Y')}")
                transferencias_criadas += 1
            else:
                print(f"   [INFO] Transferencia ENTRADA ja existe para {data_transferencia.strftime('%d/%m/%Y')}")
        
        print(f"\n[OK] Concluido!")
        print(f"   Transferencias criadas: {transferencias_criadas}")
    else:
        print(f"\n[OK] Todas as transferencias necessarias ja existem")


if __name__ == '__main__':
    print("\nEste script ira:")
    print("1. Verificar transferencias existentes da Canta Galo para Favo de Mel")
    print("2. Identificar anos faltando transferencias")
    print("3. Criar transferencias faltantes")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_corrigir_transferencias_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










