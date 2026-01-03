# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0087_add_documento_propriedade'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreferenciaModulosUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuracao', models.JSONField(default=dict, help_text='JSON com lista de módulos ativos e ordem de exibição', verbose_name='Configuração dos Módulos')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('propriedade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preferencias_modulos', to='gestao_rural.propriedade', verbose_name='Propriedade')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preferencias_modulos', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Preferência de Módulos do Usuário',
                'verbose_name_plural': 'Preferências de Módulos dos Usuários',
                'unique_together': {('usuario', 'propriedade')},
            },
        ),
    ]





