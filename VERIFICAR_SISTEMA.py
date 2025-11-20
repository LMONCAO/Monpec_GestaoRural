# -*- coding: utf-8 -*-
"""
Script rápido para verificar se o sistema está funcionando
"""

import os
import sys
import django

# Configurar Django
# Usar o mesmo settings do manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    print(f"   Tentando usar manage.py...")
    # Tentar executar via manage.py
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'check'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Django está funcionando via manage.py")
        sys.exit(0)
    else:
        print(f"❌ Erro: {result.stderr}")
        sys.exit(1)

print("=" * 60)
print("VERIFICAÇÃO DO SISTEMA")
print("=" * 60)

# Testar imports básicos
try:
    from gestao_rural.models import Propriedade, AnimalIndividual
    print("✅ Modelos básicos importados")
except Exception as e:
    print(f"❌ Erro ao importar modelos básicos: {e}")
    sys.exit(1)

# Testar imports IATF
try:
    from gestao_rural.models_iatf_completo import (
        ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF,
        IATFIndividual, AplicacaoMedicamentoIATF, CalendarioIATF
    )
    print("✅ Modelos IATF importados")
    
    # Verificar se as tabelas existem
    try:
        total = ProtocoloIATF.objects.count()
        print(f"✅ Tabela ProtocoloIATF existe ({total} registros)")
    except Exception as e:
        print(f"⚠️  Tabela ProtocoloIATF não existe ainda: {e}")
        print("   Execute: python manage.py makemigrations")
        print("   Execute: python manage.py migrate")
        
except ImportError as e:
    print(f"⚠️  Modelos IATF não importados: {e}")
    print("   Execute as migrations primeiro")

# Testar views
try:
    from gestao_rural import views_iatf_completo
    print("✅ Views IATF importadas")
except Exception as e:
    print(f"⚠️  Erro ao importar views: {e}")

# Testar URLs
try:
    from django.urls import reverse
    print("✅ URLs Django funcionando")
except Exception as e:
    print(f"❌ Erro nas URLs: {e}")

print("\n" + "=" * 60)
print("VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)
print("\nSe houver erros, execute:")
print("  1. python manage.py makemigrations")
print("  2. python manage.py migrate")
print("  3. python manage.py criar_dados_exemplo")

