# Generated migration to remove Stripe fields from model state
# This ensures Django doesn't try to query these fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0103_remover_campos_stripe'),
    ]

    operations = [
        # Migração vazia - campos já foram removidos por migrações anteriores
        # migrations.RunSQL(
        #     sql="SELECT 1;",  # Operação dummy
        #     reverse_sql="SELECT 1;"
        # ),
    ]

