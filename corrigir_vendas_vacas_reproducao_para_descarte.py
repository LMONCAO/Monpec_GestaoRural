# -*- coding: utf-8 -*-
"""
Script para corrigir vendas de vacas em reprodução.
Quando uma vaca em reprodução é vendida, ela deve:
1. Ser promovida para "Vacas Descarte +36 M" (PROMOCAO_SAIDA + PROMOCAO_ENTRADA)
2. A venda deve ser registrada como venda de "Vacas Descarte +36 M"
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
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal, VendaProjetada
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
def corrigir_vendas_vacas_reproducao_para_descarte():
    """Corrige vendas de vacas em reprodução para serem vendas de vacas descarte"""
    
    print("=" * 60)
    print("CORRIGIR VENDAS VACAS REPRODUCAO -> DESCARTE")
    print("=" * 60)
    
    # Buscar propriedade
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        print(f"\n[OK] Propriedade encontrada: {canta_galo.nome_propriedade}")
    except:
        print("[ERRO] Propriedade 'Canta Galo' nao encontrada")
        return
    
    # Buscar categorias
    try:
        categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
        categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
        print(f"[OK] Categoria Reproducao: {categoria_reproducao.nome}")
        print(f"[OK] Categoria Descarte: {categoria_descarte.nome}")
    except:
        print("[ERRO] Categorias nao encontradas")
        return
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[AVISO] Nenhum planejamento encontrado")
    else:
        print(f"[OK] Planejamento: {planejamento.codigo}")
    
    # Buscar vendas de vacas em reprodução
    vendas_reproducao = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='VENDA',
        categoria=categoria_reproducao
    ).order_by('data_movimentacao')
    
    total_vendas = vendas_reproducao.count()
    print(f"\n[INFO] Vendas de 'Vacas em Reprodução' encontradas: {total_vendas}")
    
    if total_vendas == 0:
        print("[INFO] Nenhuma venda para corrigir")
        return
    
    vendas_corrigidas = 0
    
    for venda in vendas_reproducao:
        data_venda = venda.data_movimentacao
        quantidade = venda.quantidade
        
        print(f"\n[INFO] Processando venda de {data_venda.strftime('%d/%m/%Y')}: {quantidade} cabecas")
        
        # Data da promoção: 1 dia antes da venda (ou na mesma data)
        data_promocao = data_venda - timedelta(days=1)
        if data_promocao < data_venda:
            data_promocao = data_venda
        
        # Verificar se já existe promoção para esta venda
        promocao_saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='PROMOCAO_SAIDA',
            categoria=categoria_reproducao,
            data_movimentacao=data_promocao,
            quantidade=quantidade
        ).first()
        
        if not promocao_saida_existente:
            # Criar promoção de saída (Vacas em Reprodução -> Descarte)
            promocao_saida = MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_reproducao,
                data_movimentacao=data_promocao,
                tipo_movimentacao='PROMOCAO_SAIDA',
                quantidade=quantidade,
                planejamento=planejamento,
                observacao=f'Promocao para descarte antes da venda em {data_venda.strftime("%d/%m/%Y")} (corrigido)'
            )
            print(f"   [OK] Promocao SAIDA criada: {quantidade} em {data_promocao.strftime('%d/%m/%Y')}")
        else:
            promocao_saida = promocao_saida_existente
            print(f"   [INFO] Promocao SAIDA ja existe")
        
        # Verificar se já existe promoção de entrada
        promocao_entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=data_promocao,
            quantidade=quantidade
        ).first()
        
        if not promocao_entrada_existente:
            # Criar promoção de entrada (Descarte)
            promocao_entrada = MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                data_movimentacao=data_promocao,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento,
                observacao=f'Promocao para descarte antes da venda em {data_venda.strftime("%d/%m/%Y")} (corrigido)'
            )
            print(f"   [OK] Promocao ENTRADA criada: {quantidade} em {data_promocao.strftime('%d/%m/%Y')}")
        else:
            print(f"   [INFO] Promocao ENTRADA ja existe")
        
        # Verificar se a venda já está na categoria correta
        if venda.categoria == categoria_descarte:
            print(f"   [INFO] Venda ja esta na categoria correta (Descarte)")
        else:
            # Buscar venda projetada associada
            venda_projetada = VendaProjetada.objects.filter(
                movimentacao_projetada=venda
            ).first()
            
            # Alterar categoria da venda
            venda.categoria = categoria_descarte
            venda.observacao = f'{venda.observacao or ""} - Corrigido: venda de vacas descarte (eram reprodução)'.strip()
            venda.save()
            
            if venda_projetada:
                venda_projetada.categoria = categoria_descarte
                venda_projetada.save()
            
            print(f"   [OK] Venda alterada para categoria 'Vacas Descarte'")
            vendas_corrigidas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de vendas processadas: {total_vendas}")
    print(f"   Vendas corrigidas: {vendas_corrigidas}")


if __name__ == '__main__':
    print("\nEste script ira:")
    print("1. Buscar vendas de 'Vacas em Reprodução' na Fazenda Canta Galo")
    print("2. Criar promocoes (SAIDA de Reproducao + ENTRADA em Descarte)")
    print("3. Alterar as vendas para serem de 'Vacas Descarte'")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_vendas_vacas_reproducao_para_descarte()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











