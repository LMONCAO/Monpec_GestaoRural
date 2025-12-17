# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir referências à categoria "Bezerro(a) 0-12 M" que não existe.
As categorias corretas são:
- "Bezerro(a) 0-12 F" (fêmeas)
- "Bezerro(a) 0-12 M" (machos - mas pode não existir)
- "Bezerro(o) 0-12 M" (machos)
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
def verificar_e_corrigir_categoria_bezerro():
    """Verifica e corrige referências à categoria inexistente"""
    
    print("=" * 60)
    print("VERIFICAR E CORRIGIR CATEGORIA BEZERRO")
    print("=" * 60)
    
    # Listar todas as categorias de bezerros existentes
    categorias_bezerro = CategoriaAnimal.objects.filter(
        nome__icontains='Bezerro'
    ).order_by('nome')
    
    print(f"\n[INFO] Categorias de bezerros encontradas:")
    for cat in categorias_bezerro:
        print(f"   - {cat.nome} (ID: {cat.id}, Sexo: {cat.sexo})")
    
    # Buscar categoria "Bezerro(a) 0-12 M" (que pode não existir)
    try:
        categoria_inexistente = CategoriaAnimal.objects.get(nome='Bezerro(a) 0-12 M')
        print(f"\n[AVISO] Categoria 'Bezerro(a) 0-12 M' EXISTE (ID: {categoria_inexistente.id})")
        print(f"   Sexo: {categoria_inexistente.sexo}")
    except CategoriaAnimal.DoesNotExist:
        print(f"\n[OK] Categoria 'Bezerro(a) 0-12 M' NAO EXISTE (correto)")
        
        # Buscar categorias corretas
        categoria_femea = CategoriaAnimal.objects.filter(
            nome__icontains='Bezerro',
            sexo='F'
        ).filter(nome__icontains='0-12').first()
        
        categoria_macho = CategoriaAnimal.objects.filter(
            nome__icontains='Bezerro',
            sexo='M'
        ).filter(nome__icontains='0-12').first()
        
        if not categoria_macho:
            categoria_macho = CategoriaAnimal.objects.filter(
                nome__icontains='Bezerro(o)'
            ).first()
        
        print(f"\n[INFO] Categorias corretas encontradas:")
        if categoria_femea:
            print(f"   - Fêmea: {categoria_femea.nome}")
        if categoria_macho:
            print(f"   - Macho: {categoria_macho.nome}")
        
        # Verificar se há movimentações usando a categoria inexistente
        movimentacoes_erradas = MovimentacaoProjetada.objects.filter(
            categoria__nome='Bezerro(a) 0-12 M'
        )
        
        if movimentacoes_erradas.exists():
            print(f"\n[ERRO] Encontradas {movimentacoes_erradas.count()} movimentacoes com categoria inexistente!")
            print(f"   Corrigindo movimentacoes...")
            
            # Corrigir movimentações
            for mov in movimentacoes_erradas:
                # Determinar se é macho ou fêmea baseado no contexto
                # Por padrão, usar categoria macho se disponível
                if categoria_macho:
                    mov.categoria = categoria_macho
                    mov.save()
                    print(f"   [OK] Movimentacao ID {mov.id} corrigida para {categoria_macho.nome}")
                elif categoria_femea:
                    mov.categoria = categoria_femea
                    mov.save()
                    print(f"   [OK] Movimentacao ID {mov.id} corrigida para {categoria_femea.nome}")
        else:
            print(f"\n[OK] Nenhuma movimentacao encontrada com categoria inexistente")
        
        # Verificar inventários
        inventarios_errados = InventarioRebanho.objects.filter(
            categoria__nome='Bezerro(a) 0-12 M'
        )
        
        if inventarios_errados.exists():
            print(f"\n[ERRO] Encontrados {inventarios_errados.count()} inventarios com categoria inexistente!")
            print(f"   Corrigindo inventarios...")
            
            for inv in inventarios_errados:
                if categoria_macho:
                    inv.categoria = categoria_macho
                    inv.save()
                    print(f"   [OK] Inventario ID {inv.id} corrigido para {categoria_macho.nome}")
                elif categoria_femea:
                    inv.categoria = categoria_femea
                    inv.save()
                    print(f"   [OK] Inventario ID {inv.id} corrigido para {categoria_femea.nome}")
        else:
            print(f"\n[OK] Nenhum inventario encontrado com categoria inexistente")
    
    print(f"\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_corrigir_categoria_bezerro()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

