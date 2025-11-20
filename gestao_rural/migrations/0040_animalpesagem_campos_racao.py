from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0039_adiciona_numero_requisicao'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalpesagem',
            name='tipo_racao',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Tipo de ração'),
        ),
        migrations.AddField(
            model_name='animalpesagem',
            name='consumo_racao_kg_dia',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Consumo diário de ração (kg)'),
        ),
    ]












