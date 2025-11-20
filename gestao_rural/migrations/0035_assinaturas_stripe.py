from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0034_financeiro_reestruturado'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanoAssinatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, unique=True, verbose_name='Nome do plano')),
                ('slug', models.SlugField(max_length=120, unique=True, verbose_name='Slug')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('stripe_price_id', models.CharField(max_length=120, unique=True, verbose_name='Stripe Price ID')),
                ('preco_mensal_referencia', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Preço mensal de referência (R$)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Plano de Assinatura',
                'verbose_name_plural': 'Planos de Assinatura',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='AssinaturaCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDENTE', 'Pendente'), ('ATIVA', 'Ativa'), ('SUSPENSA', 'Suspensa'), ('CANCELADA', 'Cancelada'), ('INADIMPLENTE', 'Inadimplente')], default='PENDENTE', max_length=20, verbose_name='Status')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=120, verbose_name='Stripe Customer ID')),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=120, verbose_name='Stripe Subscription ID')),
                ('ultimo_checkout_id', models.CharField(blank=True, max_length=120, verbose_name='Último Checkout Session ID')),
                ('current_period_end', models.DateTimeField(blank=True, null=True, verbose_name='Fim do período atual')),
                ('cancelamento_agendado', models.BooleanField(default=False, verbose_name='Cancelamento ao término do período')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadados adicionais')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('plano', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assinaturas', to='gestao_rural.planoassinatura', verbose_name='Plano')),
                ('produtor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assinaturas', to='gestao_rural.produtorrural', verbose_name='Produtor vinculado')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assinatura', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Assinatura de Cliente',
                'verbose_name_plural': 'Assinaturas de Clientes',
                'ordering': ['-atualizado_em'],
            },
        ),
        migrations.AddIndex(
            model_name='assinaturacliente',
            index=models.Index(fields=['stripe_customer_id'], name='gestao_rura_stripe__c9bd88_idx'),
        ),
        migrations.AddIndex(
            model_name='assinaturacliente',
            index=models.Index(fields=['stripe_subscription_id'], name='gestao_rura_stripe__5b5809_idx'),
        ),
        migrations.CreateModel(
            name='TenantWorkspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=60, unique=True, verbose_name='Alias do banco')),
                ('caminho_banco', models.CharField(max_length=255, verbose_name='Caminho do banco')),
                ('status', models.CharField(choices=[('PENDENTE', 'Pendente'), ('PROVISIONANDO', 'Provisionando'), ('ATIVO', 'Ativo'), ('ERRO', 'Erro'), ('DESATIVADO', 'Desativado')], default='PENDENTE', max_length=20, verbose_name='Status')),
                ('provisionado_em', models.DateTimeField(blank=True, null=True, verbose_name='Provisionado em')),
                ('ultimo_erro', models.TextField(blank=True, verbose_name='Último erro conhecido')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadados')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('assinatura', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workspace', to='gestao_rural.assinaturacliente', verbose_name='Assinatura')),
            ],
            options={
                'verbose_name': 'Workspace de Cliente',
                'verbose_name_plural': 'Workspaces de Clientes',
                'ordering': ['-criado_em'],
            },
        ),
    ]

