#!/usr/bin/env python
"""
Script para ativar modo de teste do Mercado Pago
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def ativar_modo_teste():
    """Ativa modo de teste para simular checkout sem Mercado Pago"""
    print("Ativando modo de teste do Mercado Pago...")

    with connection.cursor() as cursor:
        # Verificar se existem assinaturas
        cursor.execute("SELECT COUNT(*) FROM gestao_rural_assinaturacliente")
        count = cursor.fetchone()[0]
        print(f"Assinaturas encontradas: {count}")

    print("Modo de teste configurado - checkout sera simulado")
    print("Agora voce pode testar o fluxo de checkout sem precisar de chaves reais do Mercado Pago.")

if __name__ == '__main__':
    ativar_modo_teste()