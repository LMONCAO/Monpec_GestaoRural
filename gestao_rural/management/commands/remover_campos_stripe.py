from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Remove campos do Stripe do banco de dados'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Verificar se as colunas existem
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='gestao_rural_assinaturacliente' 
                    AND column_name LIKE '%stripe%'
                """)
                colunas_existentes = [row[0] for row in cursor.fetchall()]
                
                if colunas_existentes:
                    self.stdout.write(f'Colunas encontradas: {colunas_existentes}')
                    
                    # Remover colunas
                    if 'stripe_customer_id' in colunas_existentes:
                        cursor.execute("""
                            ALTER TABLE gestao_rural_assinaturacliente 
                            DROP COLUMN stripe_customer_id;
                        """)
                        self.stdout.write(self.style.SUCCESS('Coluna stripe_customer_id removida'))
                    
                    if 'stripe_subscription_id' in colunas_existentes:
                        cursor.execute("""
                            ALTER TABLE gestao_rural_assinaturacliente 
                            DROP COLUMN stripe_subscription_id;
                        """)
                        self.stdout.write(self.style.SUCCESS('Coluna stripe_subscription_id removida'))
                else:
                    self.stdout.write('Nenhuma coluna do Stripe encontrada')
                
                # Remover índices
                indices = [
                    'gestao_rura_stripe__c9bd88_idx',
                    'gestao_rura_stripe__5b5809_idx',
                    'gestao_rura_stripe__628be9_idx',
                    'gestao_rura_stripe__9724d3_idx',
                ]
                
                for indice in indices:
                    try:
                        cursor.execute(f"DROP INDEX IF EXISTS {indice};")
                        self.stdout.write(f'Índice {indice} removido (se existia)')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Erro ao remover índice {indice}: {e}'))
                
                # Remover campo do PlanoAssinatura
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='gestao_rural_planoassinatura' 
                    AND column_name LIKE '%stripe%'
                """)
                colunas_plano = [row[0] for row in cursor.fetchall()]
                
                if 'stripe_price_id' in colunas_plano:
                    cursor.execute("""
                        ALTER TABLE gestao_rural_planoassinatura 
                        DROP COLUMN stripe_price_id;
                    """)
                    self.stdout.write(self.style.SUCCESS('Coluna stripe_price_id removida'))
                
                self.stdout.write(self.style.SUCCESS('\n✅ Processo concluído com sucesso!'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro: {e}'))
                raise







