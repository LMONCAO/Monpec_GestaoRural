from django.db import migrations, models
from django.utils import timezone


def preencher_numeros(apps, schema_editor):
    Requisicao = apps.get_model('gestao_rural', 'RequisicaoCompra')
    contador = {}
    for requisicao in Requisicao.objects.order_by('propriedade_id', 'criado_em', 'id'):
        ano = (requisicao.criado_em or timezone.now()).year
        chave = (requisicao.propriedade_id, ano)
        contador[chave] = contador.get(chave, 0) + 1
        requisicao.numero = f"REQ-{ano}/{contador[chave]:04d}"
        requisicao.save(update_fields=['numero'])


def desfazer_numeros(apps, schema_editor):
    Requisicao = apps.get_model('gestao_rural', 'RequisicaoCompra')
    Requisicao.objects.update(numero=None)


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0038_adiciona_categoria_financeira_planoconta'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisicaocompra',
            name='numero',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True, verbose_name='Número da Requisição'),
        ),
        migrations.RunPython(preencher_numeros, desfazer_numeros),
    ]












