# Generated manually to remove agriculture models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0041_add_numero_manejo_to_animal'),
    ]

    operations = [
        # Remover o modelo CicloProducaoAgricola primeiro (tem ForeignKey para Cultura)
        migrations.DeleteModel(
            name='CicloProducaoAgricola',
        ),
        # Remover o modelo Cultura
        migrations.DeleteModel(
            name='Cultura',
        ),
        # Atualizar o campo tipo_operacao para remover AGRICULTURA e MISTA
        migrations.AlterField(
            model_name='propriedade',
            name='tipo_operacao',
            field=models.CharField(
                choices=[('PECUARIA', 'Pecuária')],
                max_length=20,
                verbose_name='Tipo de Operação'
            ),
        ),
    ]







