#!/usr/bin/env python
"""
Script para remover manualmente os campos do Stripe do banco de dados
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def remover_campos_stripe():
    """Remove campos do Stripe do banco de dados"""
    with connection.cursor() as cursor:
        try:
            # Remover colunas se existirem
            print("Removendo coluna stripe_customer_id...")
            cursor.execute("""
                ALTER TABLE gestao_rural_assinaturacliente 
                DROP COLUMN IF EXISTS stripe_customer_id;
            """)
            
            print("Removendo coluna stripe_subscription_id...")
            cursor.execute("""
                ALTER TABLE gestao_rural_assinaturacliente 
                DROP COLUMN IF EXISTS stripe_subscription_id;
            """)
            
            print("Removendo coluna stripe_price_id...")
            cursor.execute("""
                ALTER TABLE gestao_rural_planoassinatura 
                DROP COLUMN IF EXISTS stripe_price_id;
            """)
            
            # Remover índices se existirem
            print("Removendo índices relacionados ao Stripe...")
            indices = [
                'gestao_rura_stripe__c9bd88_idx',
                'gestao_rura_stripe__5b5809_idx',
                'gestao_rura_stripe__628be9_idx',
                'gestao_rura_stripe__9724d3_idx',
            ]
            
            for indice in indices:
                try:
                    cursor.execute(f"DROP INDEX IF EXISTS {indice};")
                    print(f"  Índice {indice} removido (se existia)")
                except Exception as e:
                    print(f"  Erro ao remover índice {indice}: {e}")
            
            print("\n✅ Campos do Stripe removidos com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro ao remover campos do Stripe: {e}")
            raise

if __name__ == '__main__':
    remover_campos_stripe()







