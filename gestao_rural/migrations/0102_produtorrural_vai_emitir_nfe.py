# Generated migration for adicionar campo vai_emitir_nfe ao ProdutorRural

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0101_rename_gestao_rur_usuario_idx_gestao_rura_usuario_f00e29_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='produtorrural',
            name='vai_emitir_nfe',
            field=models.BooleanField(default=False, help_text='Marque esta opção se o produtor vai emitir NF-e', verbose_name='Vai emitir Notas Fiscais?'),
        ),
    ]
