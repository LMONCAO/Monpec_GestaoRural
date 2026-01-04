# Generated migration for adicionar campos de certificado digital ao ProdutorRural

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0081_add_usuario_ativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='produtorrural',
            name='certificado_digital',
            field=models.FileField(blank=True, help_text='Certificado digital A1 (arquivo .p12 ou .pfx) para emissão de NF-e', null=True, upload_to='certificados_digitais/', verbose_name='Certificado Digital (.p12/.pfx)'),
        ),
        migrations.AddField(
            model_name='produtorrural',
            name='senha_certificado',
            field=models.CharField(blank=True, help_text='Senha do certificado digital', max_length=255, null=True, verbose_name='Senha do Certificado'),
        ),
        migrations.AddField(
            model_name='produtorrural',
            name='certificado_valido_ate',
            field=models.DateField(blank=True, help_text='Data de validade do certificado digital', null=True, verbose_name='Certificado válido até'),
        ),
        migrations.AddField(
            model_name='produtorrural',
            name='certificado_tipo',
            field=models.CharField(blank=True, choices=[('A1', 'A1 - Arquivo'), ('A3', 'A3 - Token/Cartão')], default='A1', help_text='A1: arquivo .p12/.pfx | A3: token/cartão físico (não suportado ainda)', max_length=10, null=True, verbose_name='Tipo de Certificado'),
        ),
    ]









