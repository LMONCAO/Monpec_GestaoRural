import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.services_nfe import detectar_certificados_instalados, configurar_certificado_windows

print("=== TESTE DE CERTIFICADOS DO WINDOWS ===")

print("\n1. Testando detecção de certificados instalados...")
try:
    certificados = detectar_certificados_instalados()
    print(f"✓ Detecção executada. Encontrados: {len(certificados)} certificados")
    if certificados:
        for i, cert in enumerate(certificados[:3]):  # Mostrar até 3
            print(f"  {i+1}. {cert.get('razao_social', 'N/A')} - CNPJ: {cert.get('cnpj', 'N/A')}")
    else:
        print("  Nenhum certificado encontrado (normal se não estiver no Windows ou sem certificados)")
except Exception as e:
    print(f"✗ Erro na detecção: {e}")

print("\n2. Testando configuração de certificado (simulação)...")
# Simular um thumbprint para teste
thumbprint_teste = "0123456789ABCDEF0123456789ABCDEF01234567"
try:
    resultado = configurar_certificado_windows(thumbprint_teste)
    print(f"✓ Configuração executada: {resultado}")
except Exception as e:
    print(f"✗ Erro na configuração: {e}")

print("\n3. Testando modelo de Produtor...")
from gestao_rural.models import ProdutorRural
try:
    # Buscar ou criar um produtor para teste
    produtor = ProdutorRural.objects.filter(cpf_cnpj__isnull=False).first()
    if produtor:
        print(f"✓ Produtor encontrado: {produtor.nome}")
        print(f"  Tipo certificado: {produtor.certificado_tipo}")
        print(f"  Thumbprint: {produtor.certificado_thumbprint or 'N/A'}")
        print(f"  Emissor: {produtor.certificado_emissor or 'N/A'}")
        print(f"  Tem certificado válido: {produtor.tem_certificado_valido()}")
    else:
        print("⚠ Nenhum produtor encontrado com CNPJ")
except Exception as e:
    print(f"✗ Erro no modelo: {e}")

print("\n=== TESTE CONCLUÍDO ===")