# -*- coding: utf-8 -*-
"""
Script para criar a transferência de entrada correspondente das 512 vacas descarte na Invernada Grande em 2023
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
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
def criar_entrada_invernada_2023():
    """Cria transferência de entrada correspondente na Invernada Grande"""
    
    print("=" * 80)
    print("CRIAR ENTRADA VACAS DESCARTE INVERNADA GRANDE 2023")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar transferência de saída da Canta Galo em 15/01/2023
    saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao=date(2023, 1, 15)
    ).first()
    
    if not saida:
        print("[ERRO] Transferencia de saida nao encontrada!")
        return
    
    print(f"[INFO] Transferencia de saida encontrada:")
    print(f"  Data: {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"  Quantidade: {saida.quantidade}")
    if saida.observacao:
        obs_safe = saida.observacao.encode('ascii', 'ignore').decode('ascii')
        print(f"  Observacao: {obs_safe[:50]}")
    
    # Verificar se já existe entrada correspondente
    entrada_existente = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao=saida.data_movimentacao,
        quantidade=saida.quantidade
    ).first()
    
    if entrada_existente:
        print(f"[INFO] Entrada correspondente ja existe!")
        print(f"  Data: {entrada_existente.data_movimentacao.strftime('%d/%m/%Y')}")
        print(f"  Quantidade: {entrada_existente.quantidade}")
        return
    
    # Criar transferência de entrada
    MovimentacaoProjetada.objects.create(
        propriedade=invernada_grande,
        categoria=categoria_descarte,
        data_movimentacao=saida.data_movimentacao,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        quantidade=saida.quantidade,
        planejamento=planejamento_invernada,
        observacao=f'Transferencia de Canta Galo - {saida.quantidade} vacas descarte (ano 2023)'
    )
    
    print(f"[OK] Transferencia de entrada criada:")
    print(f"  Data: {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"  Quantidade: {saida.quantidade}")
    print(f"  Destino: {invernada_grande.nome_propriedade}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_entrada_invernada_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

