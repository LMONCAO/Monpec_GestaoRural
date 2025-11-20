import json
from django.db import migrations, models


def preparar_ciclos_para_json(apps, schema_editor):
    Propriedade = apps.get_model('gestao_rural', 'Propriedade')
    for propriedade in Propriedade.objects.all():
        valor = getattr(propriedade, 'tipo_ciclo_pecuario', None)
        if not valor:
            propriedade.tipo_ciclo_pecuario = '[]'
        elif isinstance(valor, str):
            texto = valor.strip()
            if texto.startswith('['):
                continue
            propriedade.tipo_ciclo_pecuario = json.dumps([texto])
        else:
            propriedade.tipo_ciclo_pecuario = json.dumps(list(valor))
        propriedade.save(update_fields=['tipo_ciclo_pecuario'])


def normalizar_ciclos_json(apps, schema_editor):
    Propriedade = apps.get_model('gestao_rural', 'Propriedade')
    for propriedade in Propriedade.objects.all():
        valor = getattr(propriedade, 'tipo_ciclo_pecuario', None)
        if valor is None:
            propriedade.tipo_ciclo_pecuario = []
        elif isinstance(valor, str):
            try:
                propriedade.tipo_ciclo_pecuario = json.loads(valor)
            except json.JSONDecodeError:
                propriedade.tipo_ciclo_pecuario = [valor]
        propriedade.save(update_fields=['tipo_ciclo_pecuario'])


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0025_expand_rastreabilidade_fields'),
    ]

    operations = [
        migrations.RunPython(
            preparar_ciclos_para_json,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='propriedade',
            name='tipo_ciclo_pecuario',
            field=models.JSONField(blank=True, default=list, verbose_name='Tipos de Ciclo Pecuário'),
        ),
        migrations.RunPython(
            normalizar_ciclos_json,
            reverse_code=migrations.RunPython.noop,
        ),
    ]















