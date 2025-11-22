# Generated manually to fix missing timestamp fields
# Esta migração adiciona os campos criado_em e atualizado_em ao modelo CategoriaFinanceira
# caso eles não existam no banco de dados (corrige problema de sincronização)
from django.db import migrations, models
import django.utils.timezone


def preencher_timestamps_existentes(apps, schema_editor):
    """Preenche campos criado_em e atualizado_em para registros existentes."""
    CategoriaFinanceira = apps.get_model("gestao_rural", "CategoriaFinanceira")
    db_alias = schema_editor.connection.alias
    
    # Atualizar registros que não têm timestamp
    CategoriaFinanceira.objects.using(db_alias).filter(
        criado_em__isnull=True
    ).update(criado_em=django.utils.timezone.now())
    
    CategoriaFinanceira.objects.using(db_alias).filter(
        atualizado_em__isnull=True
    ).update(atualizado_em=django.utils.timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0049_adicionar_campos_timestamp_lancamentofinanceiro'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriafinanceira',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                null=True,
                blank=True,
                verbose_name='Criado em'
            ),
        ),
        migrations.AddField(
            model_name='categoriafinanceira',
            name='atualizado_em',
            field=models.DateTimeField(
                auto_now=True,
                null=True,
                blank=True,
                verbose_name='Atualizado em'
            ),
        ),
        migrations.RunPython(
            preencher_timestamps_existentes,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='categoriafinanceira',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='Criado em'
            ),
        ),
        migrations.AlterField(
            model_name='categoriafinanceira',
            name='atualizado_em',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Atualizado em'
            ),
        ),
    ]


