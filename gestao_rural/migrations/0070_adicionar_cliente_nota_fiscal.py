# Generated manually for adding cliente field to NotaFiscal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0069_adicionar_cota_hilton_animal'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='cliente',
            field=models.ForeignKey(
                blank=True,
                help_text='Obrigatório para NF-e de saída (venda)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notas_fiscais',
                to='gestao_rural.cliente',
                verbose_name='Cliente'
            ),
        ),
        migrations.AlterField(
            model_name='notafiscal',
            name='fornecedor',
            field=models.ForeignKey(
                blank=True,
                help_text='Obrigatório para NF-e de entrada (compra)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notas_fiscais',
                to='gestao_rural.fornecedor',
                verbose_name='Fornecedor'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='notafiscal',
            unique_together=set(),
        ),
    ]

