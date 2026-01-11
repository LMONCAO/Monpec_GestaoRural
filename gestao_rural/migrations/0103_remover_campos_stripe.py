# Generated migration to remove Stripe-related fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0036_ajusteorcamentocompra_orcamentocompramensal_and_more'),
    ]

    operations = [
        # Migração vazia - campos já foram removidos por migrações anteriores
        # migrations.RunSQL(
        #     sql="SELECT 1;",  # Operação dummy
        #     reverse_sql="SELECT 1;"
        # ),
    ]

