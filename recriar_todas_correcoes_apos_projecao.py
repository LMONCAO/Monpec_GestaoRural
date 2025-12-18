# -*- coding: utf-8 -*-
"""
Script para recriar todas as correções após gerar uma nova projeção.
Recria transferências, evoluções e vendas ajustadas e vincula ao planejamento atual.
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
    CategoriaAnimal, VendaProjetada
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
def recriar_todas_correcoes():
    """Recria todas as correções e vincula ao planejamento atual"""
    
    # Buscar propriedades
    propriedades = {}
    for nome in ['Girassol', 'Invernada Grande', 'Favo de Mel', 'Canta Galo']:
        try:
            prop = Propriedade.objects.get(nome_propriedade__icontains=nome)
            propriedades[nome.lower().replace(' ', '_')] = prop
            print(f"[OK] {prop.nome_propriedade} encontrada")
        except:
            print(f"[AVISO] {nome} nao encontrada")
    
    if not propriedades:
        print("[ERRO] Nenhuma propriedade encontrada")
        return
    
    # ========== CORREÇÃO 1: Transferências Favo de Mel -> Girassol ==========
    print("\n" + "=" * 60)
    print("CORRECAO 1: Transferencias Favo de Mel -> Girassol")
    print("=" * 60)
    
    if 'favo_de_mel' in propriedades and 'girassol' in propriedades:
        favo_mel = propriedades['favo_de_mel']
        girassol = propriedades['girassol']
        
        # Buscar planejamento do Girassol
        planejamento_girassol = PlanejamentoAnual.objects.filter(
            propriedade=girassol
        ).order_by('-data_criacao', '-ano').first()
        
        if not planejamento_girassol:
            print("[AVISO] Nenhum planejamento encontrado para Girassol")
        else:
            print(f"[OK] Planejamento Girassol: {planejamento_girassol.codigo}")
            
            # Buscar categoria garrote
            try:
                categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
            except:
                categoria_garrote = CategoriaAnimal.objects.filter(nome__icontains='Garrote').first()
            
            if categoria_garrote:
                # Verificar se já existem transferências
                transferencias_existentes = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    categoria=categoria_garrote,
                    data_movimentacao__year__in=[2022, 2023]
                ).count()
                
                if transferencias_existentes == 0:
                    print("[INFO] Recriando transferencias...")
                    
                    # Criar transferências a cada 3 meses (350 cabeças)
                    datas_transferencia = [
                        date(2022, 4, 1),   # 350
                        date(2022, 7, 1),   # 350
                        date(2022, 10, 1),  # 350
                        date(2023, 1, 1),   # 130
                    ]
                    quantidades = [350, 350, 350, 130]
                    
                    for data_transf, quantidade in zip(datas_transferencia, quantidades):
                        # Saída do Favo de Mel
                        MovimentacaoProjetada.objects.create(
                            propriedade=favo_mel,
                            categoria=categoria_garrote,
                            data_movimentacao=data_transf,
                            tipo_movimentacao='TRANSFERENCIA_SAIDA',
                            quantidade=quantidade,
                            planejamento=planejamento_girassol,
                            observacao=f'Transferencia para Girassol - lote de {quantidade} (corrigido)'
                        )
                        
                        # Entrada no Girassol
                        MovimentacaoProjetada.objects.create(
                            propriedade=girassol,
                            categoria=categoria_garrote,
                            data_movimentacao=data_transf,
                            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                            quantidade=quantidade,
                            planejamento=planejamento_girassol,
                            observacao=f'Transferencia de Favo de Mel - lote de {quantidade} (corrigido)'
                        )
                    
                    print(f"   [OK] 4 transferencias criadas")
                else:
                    print(f"[INFO] {transferencias_existentes} transferencias ja existem")
                    
                    # Vincular ao planejamento se não estiverem
                    MovimentacaoProjetada.objects.filter(
                        propriedade=girassol,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                        categoria=categoria_garrote,
                        data_movimentacao__year__in=[2022, 2023],
                        planejamento__isnull=True
                    ).update(planejamento=planejamento_girassol)
    
    # ========== CORREÇÃO 2: Evoluções Garrote -> Boi ==========
    print("\n" + "=" * 60)
    print("CORRECAO 2: Evolucoes Garrote -> Boi 24-36 M")
    print("=" * 60)
    
    if 'girassol' in propriedades:
        girassol = propriedades['girassol']
        planejamento_girassol = PlanejamentoAnual.objects.filter(
            propriedade=girassol
        ).order_by('-data_criacao', '-ano').first()
        
        if planejamento_girassol:
            try:
                categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
                categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
            except:
                print("[AVISO] Categorias nao encontradas")
            else:
                # Buscar transferências de entrada
                transferencias = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    categoria=categoria_garrote,
                    data_movimentacao__year__in=[2022, 2023]
                ).order_by('data_movimentacao')
                
                evolucoes_criadas = 0
                
                for transferencia in transferencias:
                    data_transferencia = transferencia.data_movimentacao
                    quantidade = transferencia.quantidade
                    
                    # Evolução 12 meses após
                    data_evolucao = adicionar_meses(data_transferencia, 12)
                    data_evolucao = date(data_evolucao.year, data_evolucao.month, 1)
                    
                    # Verificar se já existe
                    evolucao_existente = MovimentacaoProjetada.objects.filter(
                        propriedade=girassol,
                        tipo_movimentacao='PROMOCAO_SAIDA',
                        categoria=categoria_garrote,
                        data_movimentacao=data_evolucao,
                        quantidade=quantidade
                    ).first()
                    
                    if not evolucao_existente:
                        # Criar promoção de saída
                        MovimentacaoProjetada.objects.create(
                            propriedade=girassol,
                            categoria=categoria_garrote,
                            data_movimentacao=data_evolucao,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            quantidade=quantidade,
                            planejamento=planejamento_girassol,
                            observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (corrigido)'
                        )
                        
                        # Criar promoção de entrada
                        MovimentacaoProjetada.objects.create(
                            propriedade=girassol,
                            categoria=categoria_boi,
                            data_movimentacao=data_evolucao,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            quantidade=quantidade,
                            planejamento=planejamento_girassol,
                            observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (corrigido)'
                        )
                        
                        evolucoes_criadas += 1
                        print(f"   [OK] Evolucao criada: {quantidade} em {data_evolucao.strftime('%d/%m/%Y')}")
                    else:
                        # Vincular ao planejamento se não estiver
                        if evolucao_existente.planejamento != planejamento_girassol:
                            MovimentacaoProjetada.objects.filter(
                                propriedade=girassol,
                                tipo_movimentacao__in=['PROMOCAO_SAIDA', 'PROMOCAO_ENTRADA'],
                                categoria__in=[categoria_garrote, categoria_boi],
                                data_movimentacao=data_evolucao
                            ).update(planejamento=planejamento_girassol)
                            print(f"   [OK] Evolucao vinculada ao planejamento")
                
                if evolucoes_criadas == 0:
                    print("[INFO] Todas as evolucoes ja existem")
    
    # ========== CORREÇÃO 3: Vendas Invernada Grande ==========
    print("\n" + "=" * 60)
    print("CORRECAO 3: Vendas Invernada Grande")
    print("=" * 60)
    
    if 'invernada_grande' in propriedades:
        invernada_grande = propriedades['invernada_grande']
        
        planejamento_invernada = PlanejamentoAnual.objects.filter(
            propriedade=invernada_grande
        ).order_by('-data_criacao', '-ano').first()
        
        if planejamento_invernada:
            print(f"[OK] Planejamento Invernada Grande: {planejamento_invernada.codigo}")
            
            try:
                categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
            except:
                categoria_descarte = CategoriaAnimal.objects.filter(nome__icontains='Descarte').first()
            
            if categoria_descarte:
                # Verificar se já existem vendas
                vendas_existentes = MovimentacaoProjetada.objects.filter(
                    propriedade=invernada_grande,
                    tipo_movimentacao='VENDA',
                    categoria=categoria_descarte,
                    data_movimentacao__year=2022
                ).count()
                
                if vendas_existentes == 0:
                    print("[INFO] Recriando vendas mensais...")
                    
                    # Criar vendas mensais de 80 cabeças (fev-ago/2022)
                    quantidades = [80, 80, 80, 80, 80, 80, 32]  # 6x80 + 1x32 = 512
                    meses = [2, 3, 4, 5, 6, 7, 8]
                    
                    for mes, quantidade in zip(meses, quantidades):
                        data_venda = date(2022, mes, 1)
                        
                        peso_medio_kg = Decimal('450.00')
                        valor_por_kg = Decimal('6.50')
                        valor_por_animal = valor_por_kg * peso_medio_kg
                        valor_total = valor_por_animal * Decimal(str(quantidade))
                        
                        # Criar movimentação de venda
                        movimentacao = MovimentacaoProjetada.objects.create(
                            propriedade=invernada_grande,
                            categoria=categoria_descarte,
                            data_movimentacao=data_venda,
                            tipo_movimentacao='VENDA',
                            quantidade=quantidade,
                            valor_por_cabeca=valor_por_animal,
                            valor_total=valor_total,
                            planejamento=planejamento_invernada,
                            observacao=f'Venda mensal lote - {quantidade} vacas descarte para JBS (corrigido)'
                        )
                        
                        # Criar venda projetada
                        VendaProjetada.objects.create(
                            propriedade=invernada_grande,
                            categoria=categoria_descarte,
                            movimentacao_projetada=movimentacao,
                            data_venda=data_venda,
                            quantidade=quantidade,
                            cliente_nome='JBS',
                            peso_medio_kg=peso_medio_kg,
                            peso_total_kg=peso_medio_kg * Decimal(str(quantidade)),
                            valor_por_kg=valor_por_kg,
                            valor_por_animal=valor_por_animal,
                            valor_total=valor_total,
                            data_recebimento=data_venda + timedelta(days=30),
                            observacoes=f'Venda mensal lote - {quantidade} vacas descarte para JBS (corrigido)'
                        )
                    
                    print(f"   [OK] 7 vendas criadas")
                else:
                    print(f"[INFO] {vendas_existentes} vendas ja existem")
                    
                    # Vincular ao planejamento se não estiverem
                    MovimentacaoProjetada.objects.filter(
                        propriedade=invernada_grande,
                        tipo_movimentacao='VENDA',
                        categoria=categoria_descarte,
                        data_movimentacao__year=2022,
                        planejamento__isnull=True
                    ).update(planejamento=planejamento_invernada)
    
    print("\n" + "=" * 60)
    print("[OK] Todas as correcoes verificadas/recriadas!")
    print("=" * 60)


if __name__ == '__main__':
    print("=" * 60)
    print("RECRIAR TODAS AS CORRECOES APOS PROJECAO")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Verificar se as correcoes existem")
    print("2. Recriar se necessario")
    print("3. Vincular ao planejamento atual")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        recriar_todas_correcoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















