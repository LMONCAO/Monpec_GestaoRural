# -*- coding: utf-8 -*-
"""
Script para corrigir a categoria "Bezerro(a) 0-12 M" que tem sexo='F' mas nome sugere macho.
Opções:
1. Renomear para "Bezerro(a) 0-12 F" (se for fêmea)
2. Corrigir sexo para 'M' (se for macho)
3. Migrar para categoria correta existente
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
    CategoriaAnimal, MovimentacaoProjetada, InventarioRebanho
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
def corrigir_categoria_bezerro_inconsistente():
    """Corrige a categoria inconsistente"""
    
    print("=" * 60)
    print("CORRIGIR CATEGORIA BEZERRO INCONSISTENTE")
    print("=" * 60)
    
    try:
        categoria_problema = CategoriaAnimal.objects.get(nome='Bezerro(a) 0-12 M')
        print(f"\n[INFO] Categoria encontrada:")
        print(f"   Nome: {categoria_problema.nome}")
        print(f"   Sexo: {categoria_problema.sexo}")
        print(f"   ID: {categoria_problema.id}")
        
        # Verificar usos
        movimentacoes = MovimentacaoProjetada.objects.filter(categoria=categoria_problema)
        inventarios = InventarioRebanho.objects.filter(categoria=categoria_problema)
        
        print(f"\n[INFO] Usos encontrados:")
        print(f"   Movimentacoes: {movimentacoes.count()}")
        print(f"   Inventarios: {inventarios.count()}")
        
        # Buscar categoria correta
        # Se é fêmea, usar "Bezerro(a) 0-12 F"
        # Se é macho, usar "Bezerro(o) 0-12 M"
        
        if categoria_problema.sexo == 'F':
            # É fêmea, então deve ser "Bezerro(a) 0-12 F"
            try:
                categoria_correta = CategoriaAnimal.objects.get(nome='Bezerro(a) 0-12 F')
                print(f"\n[INFO] Categoria correta encontrada: {categoria_correta.nome}")
                
                # Migrar movimentações
                if movimentacoes.exists():
                    print(f"\n[INFO] Migrando {movimentacoes.count()} movimentacoes...")
                    movimentacoes.update(categoria=categoria_correta)
                    print(f"   [OK] Movimentacoes migradas")
                
                # Migrar inventários (tratando duplicatas)
                if inventarios.exists():
                    print(f"\n[INFO] Migrando {inventarios.count()} inventarios...")
                    for inv in inventarios:
                        # Verificar se já existe inventário com a categoria correta
                        inv_existente = InventarioRebanho.objects.filter(
                            propriedade=inv.propriedade,
                            categoria=categoria_correta,
                            data_inventario=inv.data_inventario
                        ).first()
                        
                        if inv_existente:
                            # Somar quantidades e deletar o duplicado
                            inv_existente.quantidade += inv.quantidade
                            inv_existente.save()
                            inv.delete()
                            print(f"   [OK] Inventario ID {inv.id} mesclado com existente (total: {inv_existente.quantidade})")
                        else:
                            # Migrar normalmente
                            inv.categoria = categoria_correta
                            inv.save()
                            print(f"   [OK] Inventario ID {inv.id} migrado")
                    print(f"   [OK] Inventarios migrados")
                
                # Deletar categoria inconsistente
                print(f"\n[INFO] Deletando categoria inconsistente...")
                categoria_problema.delete()
                print(f"   [OK] Categoria deletada")
                
            except CategoriaAnimal.DoesNotExist:
                # Renomear a categoria
                print(f"\n[INFO] Renomeando categoria para 'Bezerro(a) 0-12 F'...")
                categoria_problema.nome = 'Bezerro(a) 0-12 F'
                categoria_problema.save()
                print(f"   [OK] Categoria renomeada")
        
        elif categoria_problema.sexo == 'M':
            # É macho, então deve ser "Bezerro(o) 0-12 M"
            try:
                categoria_correta = CategoriaAnimal.objects.get(nome='Bezerro(o) 0-12 M')
                print(f"\n[INFO] Categoria correta encontrada: {categoria_correta.nome}")
                
                # Migrar movimentações
                if movimentacoes.exists():
                    print(f"\n[INFO] Migrando {movimentacoes.count()} movimentacoes...")
                    movimentacoes.update(categoria=categoria_correta)
                    print(f"   [OK] Movimentacoes migradas")
                
                # Migrar inventários (tratando duplicatas)
                if inventarios.exists():
                    print(f"\n[INFO] Migrando {inventarios.count()} inventarios...")
                    for inv in inventarios:
                        # Verificar se já existe inventário com a categoria correta
                        inv_existente = InventarioRebanho.objects.filter(
                            propriedade=inv.propriedade,
                            categoria=categoria_correta,
                            data_inventario=inv.data_inventario
                        ).first()
                        
                        if inv_existente:
                            # Somar quantidades e deletar o duplicado
                            inv_existente.quantidade += inv.quantidade
                            inv_existente.save()
                            inv.delete()
                            print(f"   [OK] Inventario ID {inv.id} mesclado com existente (total: {inv_existente.quantidade})")
                        else:
                            # Migrar normalmente
                            inv.categoria = categoria_correta
                            inv.save()
                            print(f"   [OK] Inventario ID {inv.id} migrado")
                    print(f"   [OK] Inventarios migrados")
                
                # Deletar categoria inconsistente
                print(f"\n[INFO] Deletando categoria inconsistente...")
                categoria_problema.delete()
                print(f"   [OK] Categoria deletada")
                
            except CategoriaAnimal.DoesNotExist:
                # Renomear a categoria
                print(f"\n[INFO] Renomeando categoria para 'Bezerro(o) 0-12 M'...")
                categoria_problema.nome = 'Bezerro(o) 0-12 M'
                categoria_problema.sexo = 'M'
                categoria_problema.save()
                print(f"   [OK] Categoria renomeada e sexo corrigido")
        
        print(f"\n[OK] Correcao concluida!")
        
    except CategoriaAnimal.DoesNotExist:
        print(f"\n[OK] Categoria 'Bezerro(a) 0-12 M' nao existe (ja foi corrigida ou nunca existiu)")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_categoria_bezerro_inconsistente()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

