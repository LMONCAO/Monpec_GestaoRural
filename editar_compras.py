#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import ConfiguracaoVenda, Propriedade, CategoriaAnimal

def listar_compras():
    """Lista todas as compras configuradas"""
    propriedade = Propriedade.objects.first()
    compras = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade,
        tipo_reposicao='COMPRA',
        ativo=True
    )
    
    print("=== COMPRAS CONFIGURADAS ===")
    for i, compra in enumerate(compras, 1):
        print(f"{i}. ID: {compra.id}")
        print(f"   Categoria: {compra.categoria_compra.nome}")
        print(f"   Frequência: {compra.frequencia_venda}")
        print(f"   Quantidade: {compra.quantidade_compra}")
        print(f"   Valor: R$ {compra.valor_animal_compra}")
        print()
    
    return compras

def editar_compra(compra_id, novo_valor=None, nova_quantidade=None, nova_frequencia=None):
    """Edita uma compra específica"""
    try:
        compra = ConfiguracaoVenda.objects.get(id=compra_id)
        
        if novo_valor is not None:
            compra.valor_animal_compra = novo_valor
        if nova_quantidade is not None:
            compra.quantidade_compra = nova_quantidade
        if nova_frequencia is not None:
            compra.frequencia_venda = nova_frequencia
        
        compra.save()
        print(f"✅ Compra {compra_id} atualizada com sucesso!")
        return True
    except ConfiguracaoVenda.DoesNotExist:
        print(f"❌ Compra com ID {compra_id} não encontrada!")
        return False
    except Exception as e:
        print(f"❌ Erro ao editar compra: {str(e)}")
        return False

def remover_compra(compra_id):
    """Remove uma compra (marca como inativa)"""
    try:
        compra = ConfiguracaoVenda.objects.get(id=compra_id)
        compra.ativo = False
        compra.save()
        print(f"✅ Compra {compra_id} removida com sucesso!")
        return True
    except ConfiguracaoVenda.DoesNotExist:
        print(f"❌ Compra com ID {compra_id} não encontrada!")
        return False
    except Exception as e:
        print(f"❌ Erro ao remover compra: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== EDITOR DE COMPRAS ===")
    print()
    
    # Listar compras
    compras = listar_compras()
    
    if compras.exists():
        print("Exemplos de uso:")
        print("editar_compra(7, novo_valor=6000.00)  # Alterar valor da compra ID 7")
        print("editar_compra(8, nova_quantidade=10)   # Alterar quantidade da compra ID 8")
        print("remover_compra(9)                      # Remover compra ID 9")
        print()
        print("Para usar, execute:")
        print("python -c \"from editar_compras import *; editar_compra(7, novo_valor=6000.00)\"")
    else:
        print("Nenhuma compra configurada.")



