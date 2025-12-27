# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestao_rural', '0079_assinaturacliente_data_liberacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuarioAtivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_completo', models.CharField(max_length=255, verbose_name='Nome Completo')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('telefone', models.CharField(blank=True, max_length=20, verbose_name='Telefone')),
                ('primeiro_acesso', models.DateTimeField(auto_now_add=True, verbose_name='Primeiro Acesso')),
                ('ultimo_acesso', models.DateTimeField(auto_now=True, verbose_name='Último Acesso')),
                ('total_acessos', models.PositiveIntegerField(default=0, verbose_name='Total de Acessos')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_ativo', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Usuário Ativo',
                'verbose_name_plural': 'Usuários Ativos',
                'ordering': ['-ultimo_acesso'],
            },
        ),
    ]

