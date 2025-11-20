# Generated manually for WhatsApp integration - Tipo de Registro
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0046_add_whatsapp_mensagens'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensagemwhatsapp',
            name='tipo_registro',
            field=models.CharField(
                choices=[
                    ('NASCIMENTO', 'Nascimento'),
                    ('SUPLEMENTACAO', 'Distribuição de Suplementação'),
                    ('OUTROS', 'Outros')
                ],
                default='NASCIMENTO',
                max_length=30,
                verbose_name='Tipo de Registro'
            ),
        ),
    ]




