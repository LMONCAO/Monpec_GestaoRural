# -*- coding: utf-8 -*-
"""
Script para testar o sistema completo
Execute: python testar_sistema_completo.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, AnimalIndividual
)

def testar_imports():
    """Testa se todos os imports estão funcionando"""
    print("=" * 60)
    print("TESTE 1: Verificando Imports")
    print("=" * 60)
    
    try:
        from gestao_rural.models_iatf_completo import (
            ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF,
            IATFIndividual, AplicacaoMedicamentoIATF, CalendarioIATF
        )
        print("✅ Módulo IATF completo importado com sucesso!")
        return True
    except ImportError as e:
        print(f"⚠️  Módulo IATF completo não encontrado: {e}")
        print("   Execute: python manage.py makemigrations")
        return False

def testar_views():
    """Testa se as views estão acessíveis"""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificando Views")
    print("=" * 60)
    
    try:
        from gestao_rural import views_iatf_completo
        print("✅ Views IATF completo importadas com sucesso!")
        
        # Verificar se as funções existem
        funcoes_necessarias = [
            'iatf_dashboard',
            'lote_iatf_novo',
            'lote_iatf_detalhes',
            'iatf_individual_novo',
            'iatf_individual_detalhes',
        ]
        
        for func in funcoes_necessarias:
            if hasattr(views_iatf_completo, func):
                print(f"   ✅ {func} encontrada")
            else:
                print(f"   ❌ {func} NÃO encontrada")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar views: {e}")
        return False

def testar_urls():
    """Testa se as URLs estão configuradas"""
    print("\n" + "=" * 60)
    print("TESTE 3: Verificando URLs")
    print("=" * 60)
    
    try:
        from django.urls import reverse
        from gestao_rural.models import Propriedade
        
        # Verificar se existe pelo menos uma propriedade
        propriedades = Propriedade.objects.all()
        if propriedades.exists():
            prop = propriedades.first()
            print(f"✅ Propriedade encontrada: {prop.nome_propriedade}")
            
            # Tentar resolver URLs
            try:
                url = reverse('iatf_dashboard', args=[prop.id])
                print(f"   ✅ URL iatf_dashboard: {url}")
            except Exception as e:
                print(f"   ⚠️  URL iatf_dashboard não configurada: {e}")
            
            return True
        else:
            print("⚠️  Nenhuma propriedade encontrada. Execute: python manage.py criar_dados_exemplo")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar URLs: {e}")
        return False

def testar_modelos():
    """Testa se os modelos estão funcionando"""
    print("\n" + "=" * 60)
    print("TESTE 4: Verificando Modelos")
    print("=" * 60)
    
    try:
        from gestao_rural.models_iatf_completo import ProtocoloIATF
        
        # Contar protocolos
        total = ProtocoloIATF.objects.count()
        print(f"✅ Modelo ProtocoloIATF funcionando! Total: {total}")
        
        # Criar um protocolo de teste
        protocolo, created = ProtocoloIATF.objects.get_or_create(
            nome='Teste Ovsynch',
            defaults={
                'tipo': 'OVSYNCH',
                'dia_gnrh': 0,
                'dia_pgf2a': 7,
                'dia_gnrh_final': 9,
                'dia_iatf': 10,
                'taxa_prenhez_esperada': Decimal('50.00'),
                'custo_protocolo': Decimal('150.00')
            }
        )
        
        if created:
            print(f"   ✅ Protocolo de teste criado: {protocolo.nome}")
        else:
            print(f"   ℹ️  Protocolo de teste já existe: {protocolo.nome}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar modelos: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_templates():
    """Testa se os templates existem"""
    print("\n" + "=" * 60)
    print("TESTE 5: Verificando Templates")
    print("=" * 60)
    
    templates_necessarios = [
        'gestao_rural/iatf_dashboard.html',
        'gestao_rural/lote_iatf_detalhes.html',
        'gestao_rural/nutricao_dashboard.html',
        'gestao_rural/operacoes_dashboard.html',
        'gestao_rural/compras_dashboard.html',
        'gestao_rural/financeiro_dashboard.html',
    ]
    
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    encontrados = 0
    
    for template in templates_necessarios:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"   ✅ {template}")
            encontrados += 1
        else:
            print(f"   ❌ {template} NÃO encontrado")
    
    print(f"\n   Total: {encontrados}/{len(templates_necessarios)} templates encontrados")
    return encontrados == len(templates_necessarios)

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("TESTE COMPLETO DO SISTEMA")
    print("=" * 60)
    print()
    
    resultados = []
    
    resultados.append(("Imports", testar_imports()))
    resultados.append(("Views", testar_views()))
    resultados.append(("URLs", testar_urls()))
    resultados.append(("Modelos", testar_modelos()))
    resultados.append(("Templates", testar_templates()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome:20} {status}")
    
    total_passou = sum(1 for _, r in resultados if r)
    total_testes = len(resultados)
    
    print(f"\nTotal: {total_passou}/{total_testes} testes passaram")
    
    if total_passou == total_testes:
        print("\n🎉 SISTEMA PRONTO PARA USO!")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")

if __name__ == '__main__':
    main()


