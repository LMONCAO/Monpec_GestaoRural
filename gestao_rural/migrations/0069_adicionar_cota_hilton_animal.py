# Generated manually on 2025-12-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0068_adicionar_multi_proprietarios_fazendas'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalindividual',
            name='cota_hilton',
            field=models.CharField(
                blank=True,
                help_text='Classificação automática baseada na categoria e características do animal',
                max_length=80,
                null=True,
                verbose_name='Cota Hilton'
            ),
        ),
    ]


