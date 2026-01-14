import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

print("=== TESTANDO IMPORTS DE NFE ===")

# Testar imports da view de NFE
try:
    from gestao_rural.views_vendas import vendas_nota_fiscal_emitir
    print('✓ Importação da view vendas_nota_fiscal_emitir: OK')
except Exception as e:
    print(f'✗ Erro na importação da view: {e}')

try:
    from gestao_rural.services_nfe import emitir_nfe
    print('✓ Importação do serviço emitir_nfe: OK')
except Exception as e:
    print(f'✗ Erro na importação do serviço: {e}')

try:
    from gestao_rural.forms_completos import NotaFiscalSaidaForm
    print('✓ Importação do form NotaFiscalSaidaForm: OK')
except Exception as e:
    print(f'✗ Erro na importação do form: {e}')

try:
    from gestao_rural.models_compras_financeiro import NotaFiscal
    print('✓ Importação do model NotaFiscal: OK')
except Exception as e:
    print(f'✗ Erro na importação do model: {e}')

# Testar configuração de NFE
print("\n=== CONFIGURAÇÃO DE NFE ===")
from django.conf import settings
api_nfe = getattr(settings, 'API_NFE', None)
print(f'API_NFE configurada: {api_nfe is not None}')
if api_nfe:
    print(f'  Tipo: {api_nfe.get("TIPO", "Não definido")}')
    print(f'  Ambiente: {api_nfe.get("AMBIENTE", "Não definido")}')
    token_configurado = bool(api_nfe.get("TOKEN"))
    print(f'  Token: {"Configurado" if token_configurado else "Não configurado"}')
else:
    print('  API_NFE não está configurada nas settings')

nfe_sefaz = getattr(settings, 'NFE_SEFAZ', None)
print(f'NFE_SEFAZ configurada: {nfe_sefaz is not None}')
if nfe_sefaz:
    certificado_path = nfe_sefaz.get("CERTIFICADO_PATH")
    print(f'  Certificado: {"Configurado" if certificado_path and os.path.exists(certificado_path) else "Não configurado"}')
    print(f'  UF: {nfe_sefaz.get("UF", "Não definido")}')
    print(f'  Ambiente: {nfe_sefaz.get("AMBIENTE", "Não definido")}')
else:
    print('  NFE_SEFAZ não está configurada nas settings')

print("\n=== TESTE CONCLUÍDO ===")