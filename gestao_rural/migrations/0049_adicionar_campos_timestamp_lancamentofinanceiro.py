# Generated manually to fix missing timestamp fields
# Esta migração adiciona os campos criado_em e atualizado_em ao modelo LancamentoFinanceiro
# caso eles não existam no banco de dados (corrige problema de sincronização)
from django.db import migrations, models
import django.utils.timezone


def preencher_timestamps_existentes(apps, schema_editor):
    """Preenche campos criado_em e atualizado_em para registros existentes."""
    LancamentoFinanceiro = apps.get_model("gestao_rural", "LancamentoFinanceiro")
    db_alias = schema_editor.connection.alias
    
    # Atualizar registros que não têm timestamp
    LancamentoFinanceiro.objects.using(db_alias).filter(
        criado_em__isnull=True
    ).update(criado_em=django.utils.timezone.now())
    
    LancamentoFinanceiro.objects.using(db_alias).filter(
        atualizado_em__isnull=True
    ).update(atualizado_em=django.utils.timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0048_curralsessao_nome_lote_curralsessao_pasto_origem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lancamentofinanceiro',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                null=True,
                blank=True,
                verbose_name='Criado em'
            ),
        ),
        migrations.AddField(
            model_name='lancamentofinanceiro',
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
            model_name='lancamentofinanceiro',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='Criado em'
            ),
        ),
        migrations.AlterField(
            model_name='lancamentofinanceiro',
            name='atualizado_em',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Atualizado em'
            ),
        ),
    ]
