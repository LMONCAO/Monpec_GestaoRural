# Generated manually for creating NumeroSequencialNFE model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0084_adicionar_campos_cancelamento_nfe'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumeroSequencialNFE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serie', models.CharField(default='1', help_text="Série da nota fiscal (geralmente '1' para a série normal)", max_length=10, verbose_name='Série da NF-e')),
                ('proximo_numero', models.IntegerField(default=1, help_text='Próximo número sequencial a ser usado nesta série', verbose_name='Próximo Número')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')),
                ('observacoes', models.TextField(blank=True, help_text="Observações sobre esta série (ex: 'Série normal', 'Série de teste', etc.)", null=True, verbose_name='Observações')),
                ('propriedade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='numeros_sequenciais_nfe', to='gestao_rural.propriedade', verbose_name='Propriedade')),
            ],
            options={
                'verbose_name': 'Número Sequencial de NF-e',
                'verbose_name_plural': 'Números Sequenciais de NF-e',
                'ordering': ['propriedade', 'serie'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='numerosequencialnfe',
            unique_together={('propriedade', 'serie')},
        ),
    ]






