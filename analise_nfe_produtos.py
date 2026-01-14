import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

print('=== ANÁLISE DETALHADA: NF-e E PRODUTOS ===')
print('')

# Verificar tabelas do banco
from django.db import connection
tables = connection.introspection.table_names()
tabelas_nfe = [t for t in tables if 'nfe' in t.lower() or 'nota' in t.lower() or 'produto' in t.lower()]
print('📊 TABELAS RELACIONADAS A NF-e:')
for tabela in tabelas_nfe:
    print(f'   ✅ {tabela}')
print('')

# Verificar modelos
try:
    from gestao_rural.models import NotaFiscal, Produto, ItemNotaFiscal
    print('📋 MODELOS NF-e:')
    print('   ✅ NotaFiscal - OK')
    print('   ✅ Produto - OK')
    print('   ✅ ItemNotaFiscal - OK')
    print('')

    # Verificar campos do Produto
    print('🔍 CAMPOS DO MODELO PRODUTO:')
    campos_produto = [f.name for f in Produto._meta.fields]
    for campo in campos_produto:
        print(f'   • {campo}')
    print('')

    # Verificar produtos existentes
    produtos_count = Produto.objects.count()
    print(f'📦 PRODUTOS CADASTRADOS: {produtos_count}')
    if produtos_count > 0:
        produtos = Produto.objects.all()[:3]
        for prod in produtos:
            print(f'   ✅ {prod.nome} (Código: {prod.codigo}) - R$ {prod.preco_venda}')
    print('')

except ImportError as e:
    print(f'❌ ERRO nos modelos: {e}')
    print('')

# Verificar configurações SEFAZ
from django.conf import settings
nfe_config = getattr(settings, 'NFE_SEFAZ', {})
print('⚙️ CONFIGURAÇÕES SEFAZ:')
print(f'   Ambiente: {nfe_config.get("AMBIENTE", "homologacao")}')
print(f'   UF: {nfe_config.get("UF", "SP")}')
print(f'   Emitir direto: {nfe_config.get("USAR_DIRETO", False)}')
print('')

print('🎯 ANÁLISE COMPLETA REALIZADA!')