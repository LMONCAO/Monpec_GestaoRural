# Generated migration to add inscricao_estadual field to Fornecedor

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0085_criar_numero_sequencial_nfe'),
    ]

    operations = [
        migrations.AddField(
            model_name='fornecedor',
            name='inscricao_estadual',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Inscrição Estadual'),
        ),
    ]






