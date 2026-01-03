from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def preencher_campos_animais(apps, schema_editor):
    AnimalIndividual = apps.get_model('gestao_rural', 'AnimalIndividual')
    for animal in AnimalIndividual.objects.all().only('id', 'numero_brinco', 'codigo_sisbov', 'data_cadastro', 'data_identificacao'):
        updated = False
        if not animal.codigo_sisbov:
            animal.codigo_sisbov = animal.numero_brinco
            updated = True
        if not animal.data_identificacao and animal.data_cadastro:
            animal.data_identificacao = animal.data_cadastro.date()
            updated = True
        if updated:
            animal.save(update_fields=['codigo_sisbov', 'data_identificacao'])


def desfazer_preenchimento(apps, schema_editor):
    AnimalIndividual = apps.get_model('gestao_rural', 'AnimalIndividual')
    AnimalIndividual.objects.update(codigo_sisbov=None, data_identificacao=None)


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0024_categoriafinanceira_alter_curralevento_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='animalindividual',
            name='codigo_eletronico',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Código Eletrônico'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='codigo_sisbov',
            field=models.CharField(blank=True, help_text='Código oficial do SISBOV/PNIB', max_length=50, null=True, unique=True, verbose_name='Código SISBOV'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_identificacao',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Identificação'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_saida',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Saída'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='lote_atual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='animais_lote', to='gestao_rural.currallote', verbose_name='Lote Atual'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='motivo_saida',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Motivo da Saída'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='responsavel_tecnico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='animais_responsavel', to=settings.AUTH_USER_MODEL, verbose_name='Responsável Técnico'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='status_sanitario',
            field=models.CharField(choices=[('APTO', 'Apto'), ('QUARENTENA', 'Quarentena'), ('SUSPEITO', 'Suspeito'), ('POSITIVO', 'Positivo'), ('INDEFINIDO', 'Indefinido')], default='INDEFINIDO', max_length=20, verbose_name='Status Sanitário'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='codigo_lote',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Código do Lote de Brincos'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='codigo_rfid',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Código RFID/EID'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='data_descarte',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Descarte'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='fornecedor',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Fornecedor'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='status_motivo',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Motivo do Status'),
        ),
        migrations.AddField(
            model_name='brincoanimal',
            name='valor_unitario',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor Unitário (R$)'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='data_documento',
            field=models.DateField(blank=True, null=True, verbose_name='Data do Documento'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='documento_emissor',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Emissor do Documento'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='documento_tipo',
            field=models.CharField(choices=[('GTA', 'GTA'), ('NFE', 'Nota Fiscal'), ('PROTOCOLO_SANITARIO', 'Protocolo Sanitário'), ('OUTROS', 'Outros')], default='OUTROS', max_length=30, verbose_name='Tipo do Documento'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='motivo_detalhado',
            field=models.TextField(blank=True, null=True, verbose_name='Motivo Detalhado'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='quantidade_animais',
            field=models.PositiveIntegerField(default=1, verbose_name='Quantidade de Animais Envolvidos'),
        ),
        migrations.AddField(
            model_name='movimentacaoindividual',
            name='responsavel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimentacoes_registradas', to=settings.AUTH_USER_MODEL, verbose_name='Responsável pelo Registro'),
        ),
        migrations.RunPython(preencher_campos_animais, desfazer_preenchimento),
    ]

