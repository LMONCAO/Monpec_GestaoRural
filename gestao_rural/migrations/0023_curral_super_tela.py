# Generated manually to suport Curral Inteligente models
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0022_financeiro_dashboard_personalizacao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CurralSessao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Identificação amigável da sessão de curral', max_length=150, verbose_name='Nome da Sessão')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição / Observações')),
                ('data_inicio', models.DateTimeField(auto_now_add=True, verbose_name='Início da Sessão')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Término da Sessão')),
                ('status', models.CharField(choices=[('ABERTA', 'Aberta'), ('ENCERRADA', 'Encerrada')], default='ABERTA', max_length=10, verbose_name='Status')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sessoes_curral_criadas', to=settings.AUTH_USER_MODEL, verbose_name='Responsável')),
                ('propriedade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessoes_curral', to='gestao_rural.propriedade', verbose_name='Propriedade')),
            ],
            options={
                'verbose_name': 'Sessão de Curral',
                'verbose_name_plural': 'Sessões de Curral',
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.CreateModel(
            name='CurralLote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do Lote')),
                ('finalidade', models.CharField(choices=[('ENGORDA', 'Engorda/Cocho'), ('PASTO', 'Retorno ao Pasto'), ('VENDA', 'Venda/Leilão'), ('REPRODUCAO', 'Reprodução'), ('ISOLAMENTO', 'Isolamento/Sanidade'), ('OUTROS', 'Outros')], default='ENGORDA', max_length=20, verbose_name='Finalidade')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('ordem_exibicao', models.PositiveIntegerField(default=0, verbose_name='Ordem de Exibição')),
                ('sessao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lotes', to='gestao_rural.curralsessao', verbose_name='Sessão')),
            ],
            options={
                'verbose_name': 'Lote de Curral',
                'verbose_name_plural': 'Lotes de Curral',
                'ordering': ['sessao', 'ordem_exibicao', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='CurralEvento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_evento', models.CharField(choices=[('IDENTIFICACAO', 'Identificação / Conferência'), ('PESAGEM', 'Pesagem'), ('TROCA_BRINCO', 'Troca de Brinco'), ('REPRODUCAO', 'Protocolo Reprodutivo / IATF'), ('DIAGNOSTICO', 'Diagnóstico de Prenhez'), ('SANIDADE', 'Sanidade / Tratamento'), ('ENTRADA', 'Movimentação de Entrada'), ('SAIDA', 'Movimentação de Saída'), ('APARTACAO', 'Apartação / Lote'), ('OUTROS', 'Outros')], max_length=20, verbose_name='Tipo de Evento')),
                ('data_evento', models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')),
                ('peso_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Peso (kg)')),
                ('variacao_peso', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Variação de Peso')),
                ('brinco_anterior', models.CharField(blank=True, max_length=50, null=True, verbose_name='Brinco Anterior')),
                ('brinco_novo', models.CharField(blank=True, max_length=50, null=True, verbose_name='Brinco Novo')),
                ('prenhez_status', models.CharField(choices=[('DESCONHECIDO', 'Desconhecido'), ('AGENDADO', 'Diagnóstico Agendado'), ('PRENHA', 'Prenha'), ('NAO_PRENHA', 'Não Prenha'), ('PARTO', 'Pariu Recentemente')], default='DESCONHECIDO', max_length=15, verbose_name='Status Reprodutivo')),
                ('data_previsao_parto', models.DateField(blank=True, null=True, verbose_name='Previsão de Parto')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('dados_adicionais', models.JSONField(blank=True, null=True, verbose_name='Dados Adicionais')),
                ('animal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventos_curral', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('lote_destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos', to='gestao_rural.currallote', verbose_name='Lote Destino')),
                ('movimentacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos_curral', to='gestao_rural.movimentacaoindividual', verbose_name='Movimentação Gerada')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos_curral_registrados', to=settings.AUTH_USER_MODEL, verbose_name='Responsável')),
                ('sessao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos', to='gestao_rural.curralsessao', verbose_name='Sessão')),
            ],
            options={
                'verbose_name': 'Evento de Curral',
                'verbose_name_plural': 'Eventos de Curral',
                'ordering': ['-data_evento'],
            },
        ),
    ]
