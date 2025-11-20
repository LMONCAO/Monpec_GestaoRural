# Generated manually for WhatsApp integration
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestao_rural', '0045_adicionar_auditoria_seguranca'),
    ]

    operations = [
        migrations.CreateModel(
            name='MensagemWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_whatsapp', models.CharField(max_length=20, verbose_name='Número do WhatsApp')),
                ('tipo_mensagem', models.CharField(default='audio', max_length=20, verbose_name='Tipo de Mensagem')),
                ('tipo_registro', models.CharField(choices=[('NASCIMENTO', 'Nascimento'), ('SUPLEMENTACAO', 'Distribuição de Suplementação'), ('OUTROS', 'Outros')], default='NASCIMENTO', max_length=30, verbose_name='Tipo de Registro')),
                ('conteudo_audio_url', models.URLField(blank=True, null=True, verbose_name='URL do Áudio')),
                ('conteudo_texto', models.TextField(blank=True, null=True, verbose_name='Texto Transcrito')),
                ('dados_extraidos', models.JSONField(blank=True, default=dict, verbose_name='Dados Extraídos')),
                ('status', models.CharField(choices=[('PENDENTE', 'Pendente de Processamento'), ('PROCESSANDO', 'Processando'), ('PROCESSADO', 'Processado com Sucesso'), ('ERRO', 'Erro no Processamento'), ('AGUARDANDO_CONFIRMACAO', 'Aguardando Confirmação')], default='PENDENTE', max_length=30, verbose_name='Status')),
                ('erro_processamento', models.TextField(blank=True, null=True, verbose_name='Erro no Processamento')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('data_recebimento', models.DateTimeField(auto_now_add=True, verbose_name='Data de Recebimento')),
                ('data_processamento', models.DateTimeField(blank=True, null=True, verbose_name='Data de Processamento')),
                ('propriedade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mensagens_whatsapp', to='gestao_rural.propriedade', verbose_name='Propriedade')),
            ],
            options={
                'verbose_name': 'Mensagem WhatsApp',
                'verbose_name_plural': 'Mensagens WhatsApp',
                'ordering': ['-data_recebimento'],
            },
        ),
    ]

