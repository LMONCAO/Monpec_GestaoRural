from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0030_compras_inicial'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalindividual',
            name='apelido',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Apelido / Nome curto'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='carencia_produtos_ate',
            field=models.DateField(blank=True, null=True, verbose_name='Carência de produtos até'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='classificacao_zootecnica',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Classificação zootécnica'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='custo_aquisicao',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Custo de aquisição (R$)'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_aquisicao',
            field=models.DateField(blank=True, null=True, verbose_name='Data de aquisição'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_ultima_cobertura',
            field=models.DateField(blank=True, null=True, verbose_name='Data da última cobertura / IATF'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_ultima_diagnostico',
            field=models.DateField(blank=True, null=True, verbose_name='Data do último diagnóstico reprodutivo'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_ultima_movimentacao',
            field=models.DateField(blank=True, null=True, verbose_name='Data da última movimentação'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='data_prevista_parto',
            field=models.DateField(blank=True, null=True, verbose_name='Data prevista de parto'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='documento_saida',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Documento de Saída'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='animais/fotos/%Y/%m/', verbose_name='Foto do Animal'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='grupo_producao',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Grupo / linha de produção'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='mae',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filhos_como_mae', to='gestao_rural.animalindividual', verbose_name='Mãe'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='nivel_confinamento',
            field=models.CharField(blank=True, choices=[('BAIXO', 'Baixo'), ('MEDIO', 'Médio'), ('ALTO', 'Alto')], max_length=10, null=True, verbose_name='Nível de confinamento'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='pai',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filhos_como_pai', to='gestao_rural.animalindividual', verbose_name='Pai'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='produtividade_leite_dia',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Produção diária de leite (L)'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='proxima_vacinacao_obrigatoria',
            field=models.DateField(blank=True, null=True, verbose_name='Próxima vacinação obrigatória'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='registro_vacinal_em_dia',
            field=models.BooleanField(default=True, verbose_name='Vacinação em dia'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='reprodutor_origem',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Origem genética / reprodutor'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='sistema_criacao',
            field=models.CharField(blank=True, choices=[('PASTO', 'Pasto'), ('SEMICONFINADO', 'Semi-confinado'), ('CONFINADO', 'Confinado'), ('INTEGRADO', 'Sistema integrado')], max_length=20, null=True, verbose_name='Sistema de criação'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='status_reprodutivo',
            field=models.CharField(choices=[('INDEFINIDO', 'Indefinido'), ('VAZIA', 'Vazia'), ('PRENHE', 'Prenhe'), ('LACTACAO', 'Lactação'), ('SECAGEM', 'Secagem'), ('DESCARTE', 'Descarte')], default='INDEFINIDO', max_length=20, verbose_name='Status Reprodutivo'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='tipo_origem',
            field=models.CharField(choices=[('NASCIMENTO', 'Nascimento na propriedade'), ('COMPRA', 'Compra'), ('TRANSFERENCIA', 'Transferência'), ('AJUSTE', 'Ajuste de cadastro')], default='NASCIMENTO', max_length=20, verbose_name='Tipo de origem'),
        ),
        migrations.AddField(
            model_name='animalindividual',
            name='valor_atual_estimado',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Valor estimado atual (R$)'),
        ),
        migrations.CreateModel(
            name='AnimalVacinaAplicada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vacina', models.CharField(max_length=120, verbose_name='Vacina')),
                ('data_aplicacao', models.DateField(verbose_name='Data de aplicação')),
                ('dose', models.CharField(blank=True, max_length=60, null=True, verbose_name='Dose')),
                ('lote_produto', models.CharField(blank=True, max_length=80, null=True, verbose_name='Lote do produto')),
                ('validade_produto', models.DateField(blank=True, null=True, verbose_name='Validade do produto')),
                ('proxima_dose', models.DateField(blank=True, null=True, verbose_name='Próxima dose')),
                ('carencia_ate', models.DateField(blank=True, null=True, verbose_name='Carência até')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Registrado em')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacinas', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vacinas_registradas', to='auth.user', verbose_name='Responsável')),
            ],
            options={
                'verbose_name': 'Vacina aplicada',
                'verbose_name_plural': 'Vacinas aplicadas',
                'ordering': ['-data_aplicacao', '-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='AnimalTratamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('produto', models.CharField(max_length=150, verbose_name='Produto / Medicamento')),
                ('dosagem', models.CharField(blank=True, max_length=120, null=True, verbose_name='Dosagem')),
                ('data_inicio', models.DateField(verbose_name='Data de início')),
                ('data_fim', models.DateField(blank=True, null=True, verbose_name='Data de término')),
                ('carencia_ate', models.DateField(blank=True, null=True, verbose_name='Carência até')),
                ('motivo', models.CharField(blank=True, max_length=200, null=True, verbose_name='Motivo do tratamento')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Registrado em')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tratamentos', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tratamentos_registrados', to='auth.user', verbose_name='Responsável')),
            ],
            options={
                'verbose_name': 'Tratamento de Animal',
                'verbose_name_plural': 'Tratamentos de Animais',
                'ordering': ['-data_inicio', '-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='AnimalReproducaoEvento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_evento', models.CharField(choices=[('COBERTURA', 'Cobertura natural'), ('INSEMINACAO', 'Inseminação'), ('DIAGNOSTICO', 'Diagnóstico de prenhez'), ('PARTO', 'Parto'), ('ABORTO', 'Aborto'), ('SECAGEM', 'Secagem'), ('OUTROS', 'Outros')], max_length=20, verbose_name='Tipo de evento')),
                ('data_evento', models.DateField(verbose_name='Data do evento')),
                ('resultado', models.CharField(blank=True, max_length=120, null=True, verbose_name='Resultado')),
                ('touro_reprodutor', models.CharField(blank=True, max_length=120, null=True, verbose_name='Touro / Sêmen utilizado')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Registrado em')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos_reproducao', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos_reproducao_registrados', to='auth.user', verbose_name='Responsável')),
            ],
            options={
                'verbose_name': 'Evento reprodutivo',
                'verbose_name_plural': 'Eventos reprodutivos',
                'ordering': ['-data_evento', '-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='AnimalPesagem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_pesagem', models.DateField(verbose_name='Data da pesagem')),
                ('peso_kg', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Peso (kg)')),
                ('local', models.CharField(blank=True, max_length=120, null=True, verbose_name='Local da pesagem')),
                ('origem_registro', models.CharField(blank=True, max_length=60, null=True, verbose_name='Origem do registro')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pesagens', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pesagens_registradas', to='auth.user', verbose_name='Responsável')),
            ],
            options={
                'verbose_name': 'Pesagem de Animal',
                'verbose_name_plural': 'Pesagens de Animais',
                'ordering': ['-data_pesagem', '-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='AnimalHistoricoEvento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_evento', models.CharField(blank=True, max_length=60, null=True, verbose_name='Tipo de evento')),
                ('descricao', models.TextField(verbose_name='Descrição do evento')),
                ('data_evento', models.DateTimeField(auto_now_add=True, verbose_name='Data do registro')),
                ('origem', models.CharField(blank=True, max_length=60, null=True, verbose_name='Origem do registro')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos_historico', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos_animais_registrados', to='auth.user', verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Evento de animal',
                'verbose_name_plural': 'Eventos de animais',
                'ordering': ['-data_evento'],
            },
        ),
        migrations.CreateModel(
            name='AnimalDocumento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(max_length=60, verbose_name='Tipo de documento')),
                ('descricao', models.CharField(blank=True, max_length=200, null=True, verbose_name='Descrição')),
                ('arquivo', models.FileField(upload_to='animais/documentos/%Y/%m/', verbose_name='Arquivo')),
                ('data_upload', models.DateTimeField(auto_now_add=True, verbose_name='Data de upload')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='gestao_rural.animalindividual', verbose_name='Animal')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documentos_animais', to='auth.user', verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Documento de animal',
                'verbose_name_plural': 'Documentos de animais',
                'ordering': ['-data_upload'],
            },
        ),
    ]





