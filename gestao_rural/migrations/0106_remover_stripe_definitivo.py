# Generated migration to remove Stripe fields from model state DEFINITIVAMENTE
# Esta migration força a remoção dos campos do Stripe do estado do modelo Django

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0105_sincronizar_migracao_0034'),
    ]

    operations = [
        # Migração vazia - campos já foram removidos por migrações anteriores
        # migrations.RunSQL(
        #     sql="SELECT 1;",  # Operação dummy
        #     reverse_sql="SELECT 1;"
        # ),
    ]






