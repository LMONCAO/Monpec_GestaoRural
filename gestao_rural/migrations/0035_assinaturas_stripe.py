# Generated migration to create basic subscription models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0006_abastecimentocombustivel_ajusteorcamentocompra_and_more'),
    ]

    operations = [
        # Operação dummy para evitar erro de migração vazia
        migrations.RunSQL(
            sql="SELECT 1;",
            reverse_sql="SELECT 1;"
        ),
    ]
