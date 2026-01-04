# Generated manually to fix OperationalError
# The field data_liberacao exists in the model but not in the database

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0075_adicionar_autorizacao_excedente_orcamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='assinaturacliente',
            name='data_liberacao',
            field=models.DateField(
                blank=True,
                help_text='Data em que o acesso ao sistema será liberado (para pré-lançamentos)',
                null=True,
                verbose_name='Data de liberação do acesso'
            ),
        ),
    ]






































