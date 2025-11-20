from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0036_ajusteorcamentocompra_orcamentocompramensal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='centrocusto',
            name='tipo',
            field=models.CharField(
                default='OPERACIONAL',
                max_length=20,
                choices=[
                    ('OPERACIONAL', 'Operacional'),
                    ('ADMINISTRATIVO', 'Administrativo'),
                    ('INVESTIMENTO', 'Investimento'),
                ],
                verbose_name='Tipo',
            ),
        ),
    ]
