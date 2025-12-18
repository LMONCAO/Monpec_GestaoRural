# -*- coding: utf-8 -*-
"""
Script para vincular as correções (evoluções e vendas ajustadas) ao planejamento mais recente.
Isso garante que as correções não sejam perdidas quando uma nova projeção é gerada.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada
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
                print("[ERRO] Nao foi possivel acessar o banco de dados")
                return False
    return False


@transaction.atomic
def vincular_correcoes_ao_planejamento():
    """Vincula as correções ao planejamento mais recente"""
    
    propriedades = {
        'girassol': Propriedade.objects.filter(nome_propriedade__icontains='Girassol').first(),
        'invernada_grande': Propriedade.objects.filter(nome_propriedade__icontains='Invernada Grande').first(),
    }
    
    for nome, propriedade in propriedades.items():
        if not propriedade:
            print(f"[AVISO] Propriedade {nome} nao encontrada")
            continue
        
        print(f"\n[INFO] Processando {propriedade.nome_propriedade}...")
        
        # Buscar planejamento mais recente
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-data_criacao', '-ano').first()
        
        if not planejamento:
            print(f"   [AVISO] Nenhum planejamento encontrado para {propriedade.nome_propriedade}")
            continue
        
        print(f"   [OK] Planejamento encontrado: {planejamento.codigo} (ano {planejamento.ano})")
        
        # Buscar movimentações sem planejamento que são correções
        # Evoluções (PROMOCAO_ENTRADA/SAIDA)
        evolucoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao__in=['PROMOCAO_ENTRADA', 'PROMOCAO_SAIDA'],
            planejamento__isnull=True
        )
        
        # Vendas ajustadas (com observação de correção)
        vendas_corrigidas = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            planejamento__isnull=True,
            observacao__icontains='CORRIGIDO'
        )
        
        # Transferências de entrada (das correções)
        transferencias = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            planejamento__isnull=True,
            observacao__icontains='Transferencia'
        )
        
        total_evolucoes = evolucoes.count()
        total_vendas = vendas_corrigidas.count()
        total_transferencias = transferencias.count()
        
        print(f"   [INFO] Movimentacoes sem planejamento encontradas:")
        print(f"      - Evolucoes: {total_evolucoes}")
        print(f"      - Vendas corrigidas: {total_vendas}")
        print(f"      - Transferencias: {total_transferencias}")
        
        # Vincular ao planejamento
        total_vinculadas = 0
        
        if total_evolucoes > 0:
            evolucoes.update(planejamento=planejamento)
            total_vinculadas += total_evolucoes
            print(f"   [OK] {total_evolucoes} evolucoes vinculadas")
        
        if total_vendas > 0:
            vendas_corrigidas.update(planejamento=planejamento)
            total_vinculadas += total_vendas
            print(f"   [OK] {total_vendas} vendas corrigidas vinculadas")
        
        if total_transferencias > 0:
            transferencias.update(planejamento=planejamento)
            total_vinculadas += total_transferencias
            print(f"   [OK] {total_transferencias} transferencias vinculadas")
        
        if total_vinculadas == 0:
            print(f"   [INFO] Nenhuma movimentacao para vincular")
        else:
            print(f"   [OK] Total vinculado: {total_vinculadas} movimentacoes")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    print("=" * 60)
    print("VINCULAR CORRECOES AO PLANEJAMENTO")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Buscar o planejamento mais recente de cada propriedade")
    print("2. Vincular as correcoes (evolucoes, vendas, transferencias) ao planejamento")
    print("3. Garantir que as correcoes nao sejam perdidas ao gerar nova projecao")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        vincular_correcoes_ao_planejamento()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















