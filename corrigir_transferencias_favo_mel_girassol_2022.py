# -*- coding: utf-8 -*-
"""
Script para corrigir transferências de garrotes:
- 1180 garrotes foram transferidos para Favo de Mel em 2022
- A cada 3 meses, 350 cabeças são transferidas de Favo de Mel para Girassol até acabar o saldo
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction, connection
import time
from calendar import monthrange
from collections import defaultdict

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada, InventarioRebanho, PlanejamentoAnual
)


def calcular_rebanho_por_movimentacoes(propriedade, data_referencia):
    """Calcula o rebanho atual baseado no inventário inicial + movimentações projetadas."""
    # Buscar inventário inicial (mais recente antes da data de referência)
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    # Inicializar saldos
    saldos = defaultdict(int)
    data_inventario = None
    
    if inventario_inicial:
        # Buscar todos os inventários da mesma data
        data_inventario = inventario_inicial.data_inventario
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario
        ).select_related('categoria')
        
        # Inicializar saldos com inventário inicial
        for inv in inventarios:
            saldos[inv.categoria.nome] = inv.quantidade
    
    # Aplicar todas as movimentações até a data de referência
    # Se não há inventário, começar desde a primeira movimentação
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__lte=data_referencia,
        **filtro_data
    ).select_related('categoria').order_by('data_movimentacao')
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldos[categoria] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldos[categoria] -= mov.quantidade
            # Garantir que não fique negativo
            if saldos[categoria] < 0:
                saldos[categoria] = 0
    
    return dict(saldos)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    # Ajustar ano e mês
    while mes > 12:
        mes -= 12
        ano += 1
    
    # Ajustar dia se o mês não tiver esse dia (ex: 31 de fevereiro)
    ultimo_dia_mes = monthrange(ano, mes)[1]
    if dia > ultimo_dia_mes:
        dia = ultimo_dia_mes
    
    return date(ano, mes, dia)


def criar_transferencia(origem, destino, categoria, quantidade, data, observacao=''):
    """Cria movimentações de transferência"""
    # Saída da origem
    MovimentacaoProjetada.objects.create(
        propriedade=origem,
        categoria=categoria,
        data_movimentacao=data,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        quantidade=quantidade,
        observacao=f'Transferencia para {destino.nome_propriedade}. {observacao}'
    )
    
    # Entrada no destino
    MovimentacaoProjetada.objects.create(
        propriedade=destino,
        categoria=categoria,
        data_movimentacao=data,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        quantidade=quantidade,
        observacao=f'Transferencia de {origem.nome_propriedade}. {observacao}'
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
                print(f"[AVISO] Banco bloqueado, aguardando {intervalo}s... (tentativa {tentativa + 1}/{max_tentativas})")
                time.sleep(intervalo)
            else:
                print("[ERRO] Nao foi possivel acessar o banco de dados apos varias tentativas")
                print("       Por favor, feche o servidor Django e tente novamente")
                return False
    return False


@transaction.atomic
def corrigir_transferencias_favo_mel_girassol_2022():
    """Corrige as transferências de garrotes de Favo de Mel para Girassol em 2022"""
    
    # Buscar propriedades
    try:
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        print(f"[OK] Propriedade encontrada: {favo_mel.nome_propriedade}")
    except Propriedade.DoesNotExist:
        print("[ERRO] Propriedade 'Favo de Mel' nao encontrada")
        return
    except Propriedade.MultipleObjectsReturned:
        favo_mel = Propriedade.objects.filter(nome_propriedade__icontains='Favo de Mel').first()
        print(f"[AVISO] Multiplas propriedades encontradas, usando: {favo_mel.nome_propriedade}")
    
    try:
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"[OK] Propriedade encontrada: {girassol.nome_propriedade}")
    except Propriedade.DoesNotExist:
        print("[ERRO] Propriedade 'Girassol' nao encontrada")
        return
    except Propriedade.MultipleObjectsReturned:
        girassol = Propriedade.objects.filter(nome_propriedade__icontains='Girassol').first()
        print(f"[AVISO] Multiplas propriedades encontradas, usando: {girassol.nome_propriedade}")
    
    # Buscar Fazenda Canta Galo para verificar transferências de saída
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        print(f"[OK] Propriedade origem encontrada: {canta_galo.nome_propriedade}")
    except:
        canta_galo = None
    
    # Buscar TODAS as transferências de entrada em 2022 para identificar a categoria correta
    todas_transf_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        data_movimentacao__year=2022
    ).select_related('categoria').order_by('data_movimentacao')
    
    # Se não encontrou entrada, buscar saída na Canta Galo
    todas_transf_saida = []
    if canta_galo:
        todas_transf_saida = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            data_movimentacao__year=2022
        ).select_related('categoria').order_by('data_movimentacao')
    
    todas_transf = list(todas_transf_entrada) + list(todas_transf_saida)
    
    if not todas_transf:
        print("[ERRO] Nenhuma transferencia encontrada em 2022")
        return
    
    print(f"\n[INFO] Transferencias encontradas em 2022:")
    for t in todas_transf:
        tipo = "ENTRADA" if t.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA' else "SAIDA"
        print(f"   - {tipo} {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome} ({t.propriedade.nome_propriedade})")
    
    # Buscar transferência de 1180 garrotes
    transferencia_1180 = None
    for t in todas_transf:
        if t.quantidade == 1180:
            # Verificar se é garrote
            if 'garrote' in t.categoria.nome.lower() or '12-24' in t.categoria.nome.lower() or 'macho' in t.categoria.nome.lower():
                transferencia_1180 = t
                break
    
    if not transferencia_1180:
        # Tentar buscar a maior transferência relacionada a garrote
        for t in sorted(todas_transf, key=lambda x: x.quantidade, reverse=True):
            if 'garrote' in t.categoria.nome.lower() or '12-24' in t.categoria.nome.lower() or 'macho' in t.categoria.nome.lower():
                transferencia_1180 = t
                break
        
        if transferencia_1180 and transferencia_1180.quantidade != 1180:
            print(f"\n[AVISO] Nao encontrada transferencia de exatamente 1180 cabecas.")
            print(f"   Encontrada transferencia de {transferencia_1180.quantidade} cabecas.")
            print(f"   Usando esta transferencia automaticamente...")
    
    if not transferencia_1180:
        print("[ERRO] Nenhuma transferencia de garrote encontrada")
        return
    
    categoria_garrote = transferencia_1180.categoria
    print(f"\n[OK] Usando transferencia:")
    print(f"   Data: {transferencia_1180.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"   Quantidade: {transferencia_1180.quantidade} cabecas")
    print(f"   Categoria: {categoria_garrote.nome}")
    print(f"   Propriedade: {transferencia_1180.propriedade.nome_propriedade}")
    
    # Se a transferência foi de saída na Canta Galo, precisamos criar a entrada correspondente no Favo de Mel
    if transferencia_1180.tipo_movimentacao == 'TRANSFERENCIA_SAIDA' and transferencia_1180.propriedade != favo_mel:
        # Verificar se já existe entrada correspondente
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=transferencia_1180.data_movimentacao,
            quantidade=transferencia_1180.quantidade
        ).first()
        
        if not entrada_correspondente:
            print(f"\n[INFO] Criando transferencia de entrada correspondente no Favo de Mel...")
            entrada_correspondente = MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                data_movimentacao=transferencia_1180.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=transferencia_1180.quantidade,
                observacao=f'Transferencia de {transferencia_1180.propriedade.nome_propriedade} - {transferencia_1180.observacao or ""}'
            )
            print(f"[OK] Transferencia de entrada criada")
    
    # Verificar transferências existentes de Favo de Mel para Girassol em 2022
    transferencias_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year=2022
    )
    
    total_transferido = sum(t.quantidade for t in transferencias_existentes)
    print(f"\n[INFO] Transferencias existentes de Favo de Mel para Girassol em 2022: {transferencias_existentes.count()} movimentacoes")
    print(f"   Total transferido: {total_transferido} cabecas")
    
    # Calcular quantas cabeças ainda precisam ser transferidas
    quantidade_restante = transferencia_1180.quantidade - total_transferido
    print(f"   Quantidade restante: {quantidade_restante} cabecas")
    
    if quantidade_restante <= 0:
        print("\n[OK] Todas as transferencias ja foram feitas. Nada a fazer.")
        return
    
    # Perguntar se deve excluir transferências existentes e recriar
    print(f"\n[ATENCAO] Existem {transferencias_existentes.count()} transferencias ja registradas.")
    print("   Opcoes:")
    print("   1. Excluir transferencias existentes e criar novas (350 a cada 3 meses)")
    print("   2. Criar apenas as transferencias faltantes")
    
    # Por padrão, vamos excluir e recriar para garantir consistência
    excluir_existentes = True
    print(f"\n   -> Excluindo transferencias existentes e recriando...")
    
    if excluir_existentes:
        # Excluir transferências de saída e entrada correspondentes
        for transf_saida in transferencias_existentes:
            # Buscar e excluir entrada correspondente no Girassol
            transf_entrada = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=categoria_garrote,
                data_movimentacao=transf_saida.data_movimentacao,
                quantidade=transf_saida.quantidade
            ).first()
            
            if transf_entrada:
                transf_entrada.delete()
            
            transf_saida.delete()
        
        print(f"   Excluindo {transferencias_existentes.count()} transferencias...")
        quantidade_restante = transferencia_1180.quantidade
    
    # Criar transferências a cada 3 meses de 350 cabeças
    # Começar 3 meses após a transferência inicial
    data_transferencia_inicial = transferencia_1180.data_movimentacao
    data_primeira_transferencia = adicionar_meses(data_transferencia_inicial, 3)
    # Ajustar para o primeiro dia do mês
    data_primeira_transferencia = date(data_primeira_transferencia.year, data_primeira_transferencia.month, 1)
    
    quantidade_por_lote = 350
    quantidade_total_transferir = quantidade_restante
    
    print(f"\n[INFO] Criando transferencias a cada 3 meses:")
    print(f"   Data inicial: {data_primeira_transferencia.strftime('%d/%m/%Y')}")
    print(f"   Quantidade por lote: {quantidade_por_lote} cabecas")
    print(f"   Total a transferir: {quantidade_total_transferir} cabecas")
    
    data_transferencia = data_primeira_transferencia
    quantidade_transferida = 0
    lote_numero = 1
    max_lotes = 12  # Limite de 12 transferências (3 anos) para evitar loop infinito
    
    while quantidade_transferida < quantidade_total_transferir and lote_numero <= max_lotes:
        quantidade_lote = min(quantidade_por_lote, quantidade_total_transferir - quantidade_transferida)
        
        # Verificar estoque disponível antes de criar transferência
        saldos = calcular_rebanho_por_movimentacoes(favo_mel, data_transferencia)
        estoque_disponivel = saldos.get(categoria_garrote.nome, 0)
        
        if estoque_disponivel < quantidade_lote:
            print(f"\n[AVISO] Estoque insuficiente em {data_transferencia.strftime('%d/%m/%Y')}")
            print(f"   Estoque disponivel: {estoque_disponivel}")
            print(f"   Quantidade desejada: {quantidade_lote}")
            quantidade_lote = min(quantidade_lote, estoque_disponivel)
            
            if quantidade_lote <= 0:
                print(f"   Pulando este periodo (sem estoque)")
                data_transferencia = adicionar_meses(data_transferencia, 3)
                continue
        
        # Criar transferência
        observacao = f'Transferencia mensal lote {lote_numero} - {quantidade_lote} garrotes para Girassol (corrigido)'
        criar_transferencia(
            origem=favo_mel,
            destino=girassol,
            categoria=categoria_garrote,
            quantidade=quantidade_lote,
            data=data_transferencia,
            observacao=observacao
        )
        
        print(f"   [OK] Lote {lote_numero}: {quantidade_lote} cabecas em {data_transferencia.strftime('%d/%m/%Y')}")
        
        quantidade_transferida += quantidade_lote
        lote_numero += 1
        
        # Avançar para o próximo período (3 meses)
        data_transferencia = adicionar_meses(data_transferencia, 3)
        
        if quantidade_transferida >= quantidade_total_transferir:
            break
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de lotes criados: {lote_numero - 1}")
    print(f"   Total transferido: {quantidade_transferida} cabecas")


if __name__ == '__main__':
    print("=" * 60)
    print("CORRECAO DE TRANSFERENCIAS - FAVO DE MEL -> GIRASSOL 2022")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Buscar a transferencia de 1180 garrotes para Favo de Mel em 2022")
    print("2. Criar transferencias de Favo de Mel para Girassol a cada 3 meses (350 cabecas)")
    print("3. Comecar 3 meses apos a transferencia inicial")
    print("\n" + "=" * 60 + "\n")
    
    # Aguardar banco ficar livre
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias_favo_mel_girassol_2022()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

