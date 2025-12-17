# -*- coding: utf-8 -*-
"""
Script para deletar definitivamente a categoria 'Bezerro(a) 0-12 M' que não deveria existir
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import CategoriaAnimal, MovimentacaoProjetada, InventarioRebanho


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
def deletar_categoria_definitivo():
    """Deleta a categoria inconsistente definitivamente"""
    
    print("=" * 60)
    print("DELETAR CATEGORIA BEZERRO INCONSISTENTE DEFINITIVO")
    print("=" * 60)
    
    # Buscar todas as instâncias da categoria
    categorias_inexistentes = CategoriaAnimal.objects.filter(nome='Bezerro(a) 0-12 M')
    
    total = categorias_inexistentes.count()
    print(f"\n[INFO] Categorias 'Bezerro(a) 0-12 M' encontradas: {total}")
    
    if total == 0:
        print("[OK] Nenhuma categoria inconsistente encontrada")
        return
    
    for cat in categorias_inexistentes:
        print(f"\n[INFO] Processando categoria ID {cat.id}:")
        print(f"   Nome: {cat.nome}")
        print(f"   Sexo: {cat.sexo}")
        
        # Verificar usos
        movs = MovimentacaoProjetada.objects.filter(categoria=cat)
        invs = InventarioRebanho.objects.filter(categoria=cat)
        
        print(f"   Movimentacoes: {movs.count()}")
        print(f"   Inventarios: {invs.count()}")
        
        if movs.exists() or invs.exists():
            print(f"   [AVISO] Categoria tem usos! Migrando...")
            
            # Buscar categoria correta
            if cat.sexo == 'F':
                categoria_correta = CategoriaAnimal.objects.filter(
                    nome='Bezerro(a) 0-12 F'
                ).first()
            else:
                categoria_correta = CategoriaAnimal.objects.filter(
                    nome='Bezerro(o) 0-12 M'
                ).first()
            
            if categoria_correta:
                movs.update(categoria=categoria_correta)
                invs.update(categoria=categoria_correta)
                print(f"   [OK] Usos migrados para {categoria_correta.nome}")
            else:
                print(f"   [ERRO] Categoria correta nao encontrada!")
                continue
        
        # Deletar categoria
        cat.delete()
        print(f"   [OK] Categoria deletada")
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de categorias deletadas: {total}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        deletar_categoria_definitivo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











