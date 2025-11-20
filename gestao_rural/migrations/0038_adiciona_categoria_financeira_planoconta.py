from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0037_adiciona_tipo_centrocusto'),
    ]

    operations = [
        migrations.AddField(
            model_name='planoconta',
            name='categoria_financeira',
            field=models.ForeignKey(
                to='gestao_rural.categoriafinanceira',
                related_name='planos_conta',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
            ),
        ),
    ]












