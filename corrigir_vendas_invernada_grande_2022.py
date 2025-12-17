# -*- coding: utf-8 -*-
"""
Script para corrigir vendas de vacas descarte na Invernada Grande em 2022.
As 512 vacas descarte transferidas devem ser vendidas em lotes de 80 cabeças todo mês para JBS.
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
from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada, PlanejamentoAnual
)


def calcular_rebanho_por_movimentacoes(propriedade, data_referencia):
    """Calcula o rebanho atual baseado no inventário inicial + movimentações projetadas."""
    from collections import defaultdict
    
    # Buscar inventário inicial (mais recente antes da data de referência)
    from gestao_rural.models import InventarioRebanho
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


def criar_venda(propriedade, categoria, quantidade, data_venda, cliente_nome='JBS', 
                valor_por_kg=Decimal('6.50'), peso_medio_kg=Decimal('450.00'), observacao=''):
    """Cria uma venda projetada"""
    from datetime import timedelta
    
    peso_total = peso_medio_kg * Decimal(str(quantidade))
    valor_por_animal = valor_por_kg * peso_medio_kg
    valor_total = valor_por_animal * Decimal(str(quantidade))
    
    # Criar movimentação de venda
    movimentacao = MovimentacaoProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao=data_venda,
        tipo_movimentacao='VENDA',
        quantidade=quantidade,
        valor_por_cabeca=valor_por_animal,
        valor_total=valor_total,
        observacao=observacao
    )
    
    # Criar venda projetada
    venda = VendaProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        movimentacao_projetada=movimentacao,
        data_venda=data_venda,
        quantidade=quantidade,
        cliente_nome=cliente_nome,
        peso_medio_kg=peso_medio_kg,
        peso_total_kg=peso_total,
        valor_por_kg=valor_por_kg,
        valor_por_animal=valor_por_animal,
        valor_total=valor_total,
        data_recebimento=data_venda + timedelta(days=30),
        observacoes=observacao
    )
    
    return movimentacao, venda


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    from calendar import monthrange
    
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
def corrigir_vendas_invernada_grande_2022():
    """Corrige as vendas de vacas descarte na Invernada Grande em 2022"""
    
    # Buscar propriedades
    try:
        invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
        print(f"[OK] Propriedade encontrada: {invernada_grande.nome_propriedade}")
    except Propriedade.DoesNotExist:
        print("[ERRO] Propriedade 'Invernada Grande' nao encontrada")
        return
    except Propriedade.MultipleObjectsReturned:
        invernada_grande = Propriedade.objects.filter(nome_propriedade__icontains='Invernada Grande').first()
        print(f"[AVISO] Multiplas propriedades encontradas, usando: {invernada_grande.nome_propriedade}")
    
    # Buscar Fazenda Canta Galo para verificar transferências de saída
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        print(f"[OK] Propriedade origem encontrada: {canta_galo.nome_propriedade}")
    except:
        canta_galo = None
    
    # Buscar TODAS as transferências de entrada em 2022 para identificar a categoria correta
    todas_transf_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
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
        print("   Verificando transferencias de entrada na Invernada Grande...")
        print("   Verificando transferencias de saida na Canta Galo...")
        return
    
    print(f"\n[INFO] Transferencias encontradas em 2022:")
    for t in todas_transf:
        tipo = "ENTRADA" if t.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA' else "SAIDA"
        print(f"   - {tipo} {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome} ({t.propriedade.nome_propriedade})")
    
    # Buscar transferência de 512 cabeças
    transferencia_512 = None
    for t in todas_transf:
        if t.quantidade == 512:
            transferencia_512 = t
            break
    
    if not transferencia_512:
        # Tentar buscar a maior transferência relacionada a descarte
        for t in sorted(todas_transf, key=lambda x: x.quantidade, reverse=True):
            if 'descarte' in t.categoria.nome.lower() or 'gorda' in t.categoria.nome.lower():
                transferencia_512 = t
                break
        
        if not transferencia_512:
            # Pegar a maior transferência
            transferencia_512 = max(todas_transf, key=lambda x: x.quantidade)
        
        if transferencia_512.quantidade != 512:
            print(f"\n[AVISO] Nao encontrada transferencia de exatamente 512 cabecas.")
            print(f"   Encontrada transferencia de {transferencia_512.quantidade} cabecas.")
            print(f"   Usando esta transferencia automaticamente...")
    
    if not transferencia_512:
        print("[ERRO] Nenhuma transferencia encontrada")
        return
    
    categoria_descarte = transferencia_512.categoria
    print(f"\n[OK] Usando transferencia:")
    print(f"   Data: {transferencia_512.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"   Quantidade: {transferencia_512.quantidade} cabecas")
    print(f"   Categoria: {categoria_descarte.nome}")
    print(f"   Propriedade: {transferencia_512.propriedade.nome_propriedade}")
    
    # Se a transferência foi de saída na Canta Galo, precisamos criar a entrada correspondente na Invernada Grande
    if transferencia_512.tipo_movimentacao == 'TRANSFERENCIA_SAIDA' and transferencia_512.propriedade != invernada_grande:
        # Verificar se já existe entrada correspondente
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada_grande,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=transferencia_512.data_movimentacao,
            quantidade=transferencia_512.quantidade
        ).first()
        
        if not entrada_correspondente:
            print(f"\n[INFO] Criando transferencia de entrada correspondente na Invernada Grande...")
            entrada_correspondente = MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=transferencia_512.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=transferencia_512.quantidade,
                observacao=f'Transferencia de {transferencia_512.propriedade.nome_propriedade} - {transferencia_512.observacao or ""}'
            )
            print(f"[OK] Transferencia de entrada criada")
    
    # Usar a transferência encontrada
    # Se foi de saída, usar a entrada correspondente que criamos ou buscar
    if transferencia_512.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
        # Buscar a entrada correspondente na Invernada Grande
        transferencia_entrada = MovimentacaoProjetada.objects.filter(
            propriedade=invernada_grande,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=transferencia_512.data_movimentacao,
            quantidade=transferencia_512.quantidade
        ).first()
        
        if transferencia_entrada:
            transferencia = transferencia_entrada
        else:
            transferencia = transferencia_512
    else:
        transferencia = transferencia_512
    
    data_transferencia = transferencia.data_movimentacao
    quantidade_transferida = transferencia.quantidade
    
    print(f"\n[OK] Transferencia encontrada:")
    print(f"   Data: {data_transferencia.strftime('%d/%m/%Y')}")
    print(f"   Quantidade: {quantidade_transferida} cabeças")
    print(f"   Categoria: {categoria_descarte.nome}")
    
    # Verificar vendas existentes em 2022 para esta categoria
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte,
        data_movimentacao__year=2022
    )
    
    total_vendido = sum(v.quantidade for v in vendas_existentes)
    print(f"\n[INFO] Vendas existentes em 2022: {vendas_existentes.count()} movimentacoes")
    print(f"   Total vendido: {total_vendido} cabeças")
    
    # Calcular quantas cabeças ainda precisam ser vendidas
    quantidade_restante = quantidade_transferida - total_vendido
    print(f"   Quantidade restante: {quantidade_restante} cabeças")
    
    if quantidade_restante <= 0:
        print("\n[OK] Todas as vacas ja foram vendidas. Nada a fazer.")
        return
    
    # Perguntar se deve excluir vendas existentes e recriar
    print(f"\n[ATENCAO] Existem {vendas_existentes.count()} vendas ja registradas.")
    print("   Opções:")
    print("   1. Excluir vendas existentes e criar novas (lotes de 80/mês)")
    print("   2. Criar apenas as vendas faltantes")
    
    # Por padrão, vamos excluir e recriar para garantir consistência
    excluir_existentes = True
    print(f"\n   -> Excluindo vendas existentes e recriando...")
    
    if excluir_existentes:
        # Excluir vendas projetadas associadas
        vendas_projetadas = VendaProjetada.objects.filter(
            movimentacao_projetada__in=vendas_existentes
        )
        print(f"   Excluindo {vendas_projetadas.count()} vendas projetadas...")
        vendas_projetadas.delete()
        
        # Excluir movimentações de venda
        print(f"   Excluindo {vendas_existentes.count()} movimentações de venda...")
        vendas_existentes.delete()
        
        quantidade_restante = quantidade_transferida
    
    # Criar vendas mensais de 80 cabeças
    # Começar no mês seguinte à transferência
    data_primeira_venda = adicionar_meses(data_transferencia, 1)
    # Ajustar para o primeiro dia do mês
    data_primeira_venda = date(data_primeira_venda.year, data_primeira_venda.month, 1)
    
    quantidade_por_lote = 80
    quantidade_total_vender = quantidade_restante
    
    print(f"\n[INFO] Criando vendas mensais:")
    print(f"   Data inicial: {data_primeira_venda.strftime('%d/%m/%Y')}")
    print(f"   Quantidade por lote: {quantidade_por_lote} cabeças")
    print(f"   Total a vender: {quantidade_total_vender} cabeças")
    
    data_venda = data_primeira_venda
    quantidade_vendida = 0
    lote_numero = 1
    max_lotes = 12  # Limite de 12 meses (1 ano) para evitar loop infinito
    
    while quantidade_vendida < quantidade_total_vender and lote_numero <= max_lotes:
        quantidade_lote = min(quantidade_por_lote, quantidade_total_vender - quantidade_vendida)
        
        # Verificar estoque disponível antes de criar venda
        saldos = calcular_rebanho_por_movimentacoes(invernada_grande, data_venda)
        estoque_disponivel = saldos.get(categoria_descarte.nome, 0)
        
        if estoque_disponivel < quantidade_lote:
            print(f"\n[AVISO] Estoque insuficiente em {data_venda.strftime('%d/%m/%Y')}")
            print(f"   Estoque disponível: {estoque_disponivel}")
            print(f"   Quantidade desejada: {quantidade_lote}")
            quantidade_lote = min(quantidade_lote, estoque_disponivel)
            
            if quantidade_lote <= 0:
                print(f"   Pulando este mês (sem estoque)")
                data_venda = adicionar_meses(data_venda, 1)
                continue
        
        # Criar venda
        observacao = f'Venda mensal lote {lote_numero} - {quantidade_lote} vacas descarte para JBS (corrigido)'
        movimentacao, venda = criar_venda(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            quantidade=quantidade_lote,
            data_venda=data_venda,
            cliente_nome='JBS',
            valor_por_kg=Decimal('6.50'),
            peso_medio_kg=Decimal('450.00'),
            observacao=observacao
        )
        
        print(f"   [OK] Lote {lote_numero}: {quantidade_lote} cabecas em {data_venda.strftime('%d/%m/%Y')} - R$ {venda.valor_total:,.2f}")
        
        quantidade_vendida += quantidade_lote
        lote_numero += 1
        
        # Avançar para o próximo mês
        data_venda = adicionar_meses(data_venda, 1)
        
        if quantidade_vendida >= quantidade_total_vender:
            break
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de lotes criados: {lote_numero - 1}")
    print(f"   Total vendido: {quantidade_vendida} cabeças")
    print(f"   Valor total: R$ {sum(VendaProjetada.objects.filter(movimentacao_projetada__propriedade=invernada_grande, movimentacao_projetada__categoria=categoria_descarte, data_venda__year=2022).values_list('valor_total', flat=True)):,.2f}")


if __name__ == '__main__':
    print("=" * 60)
    print("CORRECAO DE VENDAS - INVERNADA GRANDE 2022")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Buscar a transferencia de 512 vacas descarte para Invernada Grande em 2022")
    print("2. Criar vendas mensais de 80 cabecas para JBS")
    print("3. Comecar no mes seguinte a transferencia")
    print("\n" + "=" * 60 + "\n")
    
    # Aguardar banco ficar livre
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_vendas_invernada_grande_2022()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

