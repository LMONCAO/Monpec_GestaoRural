# -*- coding: utf-8 -*-
"""
Script para verificar e configurar a projeção PROJ-2025-0074
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, PlanejamentoAnual
)


def verificar_e_configurar():
    """Verifica e configura a projeção PROJ-2025-0074"""
    
    print("=" * 80)
    print("VERIFICAR E CONFIGURAR PROJECAO PROJ-2025-0074")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0074'
    ).first()
    
    if not planejamento:
        print("\n[ERRO] Planejamento PROJ-2025-0074 não encontrado!")
        return
    
    print(f"\n[INFO] Planejamento encontrado:")
    print(f"  Código: {planejamento.codigo}")
    print(f"  Propriedade: {planejamento.propriedade.nome_propriedade}")
    print(f"  Ano: {planejamento.ano}")
    print(f"  Data criação: {planejamento.data_criacao}")
    
    # Buscar movimentações
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento=planejamento
    )
    
    print(f"\n[MOVIMENTACOES]")
    print(f"  Total: {movimentacoes.count()}")
    
    if movimentacoes.count() == 0:
        print("\n[AVISO] Nenhuma movimentação encontrada. Aplicando configurações padrão...")
        
        # Aplicar configuração padrão da Girassol
        try:
            from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol
            aplicar_configuracao_padrao_girassol(girassol, planejamento)
            print("[OK] Configuração padrão da Girassol aplicada!")
        except Exception as e:
            print(f"[ERRO] {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Verificar se há transferências do Favo de Mel
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        planejamento_favo = PlanejamentoAnual.objects.filter(
            propriedade=favo_mel
        ).order_by('-data_criacao', '-ano').first()
        
        if planejamento_favo:
            print("\n[INFO] Verificando transferências do Favo de Mel...")
            
            # Buscar transferências de saída do Favo de Mel
            from gestao_rural.models import CategoriaAnimal
            categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
            
            saidas_favo = MovimentacaoProjetada.objects.filter(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                planejamento=planejamento_favo
            ).order_by('data_movimentacao')
            
            print(f"  Transferências de saída do Favo de Mel: {saidas_favo.count()}")
            
            # Criar entradas correspondentes na Girassol
            entradas_criadas = 0
            for saida in saidas_favo:
                # Verificar se já existe entrada
                entrada_existente = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    categoria=categoria_garrote,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    data_movimentacao=saida.data_movimentacao,
                    quantidade=saida.quantidade,
                    planejamento=planejamento
                ).first()
                
                if not entrada_existente:
                    MovimentacaoProjetada.objects.create(
                        propriedade=girassol,
                        categoria=categoria_garrote,
                        data_movimentacao=saida.data_movimentacao,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                        quantidade=saida.quantidade,
                        planejamento=planejamento,
                        observacao=f'Transferencia de Favo de Mel - {saida.quantidade} garrotes - CONFIGURACAO PADRAO'
                    )
                    entradas_criadas += 1
            
            print(f"  Entradas criadas na Girassol: {entradas_criadas}")
            
            # Aplicar configuração padrão novamente para criar evoluções e vendas
            if entradas_criadas > 0:
                print("\n[Aplicando configuração padrão novamente...]")
                try:
                    from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol
                    aplicar_configuracao_padrao_girassol(girassol, planejamento)
                    print("[OK] Configuração padrão aplicada novamente!")
                except Exception as e:
                    print(f"[ERRO] {str(e)}")
                    import traceback
                    traceback.print_exc()
    
    # Verificar movimentações novamente
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento=planejamento
    )
    
    print(f"\n[MOVIMENTACOES APOS CONFIGURACAO]")
    print(f"  Total: {movimentacoes.count()}")
    
    # Agrupar por tipo
    tipos = {}
    for mov in movimentacoes:
        tipo = mov.tipo_movimentacao
        if tipo not in tipos:
            tipos[tipo] = 0
        tipos[tipo] += 1
    
    print(f"\n[TIPOS DE MOVIMENTACOES]")
    for tipo, count in sorted(tipos.items()):
        print(f"  {tipo}: {count}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar_e_configurar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











