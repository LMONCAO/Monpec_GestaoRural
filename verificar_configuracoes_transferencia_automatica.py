# -*- coding: utf-8 -*-
"""
Script para verificar configurações de transferência automática
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, ConfiguracaoVenda, CategoriaAnimal

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR CONFIGURACOES DE TRANSFERENCIA AUTOMATICA")
print("=" * 80)

# Verificar configurações de transferência
configuracoes = ConfiguracaoVenda.objects.filter(
    propriedade_origem=canta_galo,
    categoria=categoria_descarte
)

print(f"\n[INFO] Configuracoes encontradas: {configuracoes.count()}")

for config in configuracoes:
    print(f"\n  ID: {config.id}")
    print(f"  Propriedade destino: {config.propriedade_destino.nome_propriedade if config.propriedade_destino else 'N/A'}")
    print(f"  Categoria: {config.categoria.nome}")
    print(f"  Tipo: {getattr(config, 'tipo_configuracao', 'N/A')}")
    print(f"  Tipo reposicao: {getattr(config, 'tipo_reposicao', 'N/A')}")
    print(f"  Ativo: {getattr(config, 'ativo', 'N/A')}")

# Verificar também configurações onde Canta Galo é origem
configuracoes_origem = ConfiguracaoVenda.objects.filter(
    propriedade_origem=canta_galo
)

print(f"\n[INFO] Total de configuracoes com Canta Galo como origem: {configuracoes_origem.count()}")

for config in configuracoes_origem:
    print(f"\n  Categoria: {config.categoria.nome}")
    print(f"  Destino: {config.propriedade_destino.nome_propriedade if config.propriedade_destino else 'N/A'}")
    print(f"  Tipo reposicao: {getattr(config, 'tipo_reposicao', 'N/A')}")
    print(f"  Ativo: {getattr(config, 'ativo', 'N/A')}")

print(f"\n[OK] Verificacao concluida!")
























