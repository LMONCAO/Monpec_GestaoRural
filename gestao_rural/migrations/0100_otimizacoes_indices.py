# Generated manually for performance optimizations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0094_arquivokml_configuracaomarketing_folhapagamento_and_more'),  # Última migration real
    ]

    operations = [
        # Índices para ProdutorRural
        migrations.AddIndex(
            model_name='produtorrural',
            index=models.Index(fields=['usuario_responsavel', 'nome'], name='gestao_rur_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='produtorrural',
            index=models.Index(fields=['cpf_cnpj'], name='gestao_rur_cpf_cnpj_idx'),
        ),
        migrations.AddIndex(
            model_name='produtorrural',
            index=models.Index(fields=['data_cadastro'], name='gestao_rur_data_cad_idx'),
        ),
        # Índices para Propriedade
        migrations.AddIndex(
            model_name='propriedade',
            index=models.Index(fields=['produtor', 'nome_propriedade'], name='gestao_rur_prod_nome_idx'),
        ),
        migrations.AddIndex(
            model_name='propriedade',
            index=models.Index(fields=['produtor', 'tipo_operacao'], name='gestao_rur_prod_tipo_idx'),
        ),
        migrations.AddIndex(
            model_name='propriedade',
            index=models.Index(fields=['data_cadastro'], name='gestao_rur_prop_data_idx'),
        ),
    ]

