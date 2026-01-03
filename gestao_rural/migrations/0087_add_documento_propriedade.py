# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0086_adicionar_inscricao_estadual_fornecedor'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoPropriedade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(choices=[('MATRICULA', 'Matrícula'), ('ITR', 'ITR - Imposto Territorial Rural'), ('CCIR', 'CCIR - Certificado de Cadastro de Imóvel Rural'), ('CAR', 'CAR - Cadastro Ambiental Rural'), ('CERTIDAO_NEGATIVA', 'Certidão Negativa'), ('CONTRATO', 'Contrato'), ('LAUDO', 'Laudo'), ('OUTROS', 'Outros')], max_length=30, verbose_name='Tipo de Documento')),
                ('nome_documento', models.CharField(max_length=200, verbose_name='Nome do Documento')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('arquivo', models.FileField(upload_to='propriedades/documentos/%Y/%m/', verbose_name='Arquivo PDF')),
                ('data_upload', models.DateTimeField(auto_now_add=True, verbose_name='Data de Upload')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('data_vencimento', models.DateField(blank=True, null=True, verbose_name='Data de Vencimento')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documentos_criados', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('propriedade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='gestao_rural.propriedade', verbose_name='Propriedade')),
            ],
            options={
                'verbose_name': 'Documento da Propriedade',
                'verbose_name_plural': 'Documentos da Propriedade',
                'ordering': ['-data_upload'],
            },
        ),
        migrations.AddIndex(
            model_name='documentopropriedade',
            index=models.Index(fields=['propriedade', 'tipo_documento'], name='gestao_rur_proprie_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='documentopropriedade',
            index=models.Index(fields=['data_vencimento'], name='gestao_rur_data_ve_12345_idx'),
        ),
    ]

