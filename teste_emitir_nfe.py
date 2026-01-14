import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.services_nfe import emitir_nfe
from django.utils import timezone
from decimal import Decimal

# Criar um mock de nota fiscal
class MockProdutor:
    def __init__(self):
        self.certificado_digital = None

    def tem_certificado_valido(self):
        return False

class MockPropriedade:
    def __init__(self):
        self.cnpj = '12345678000123'
        self.nome_propriedade = 'Fazenda Teste'
        self.produtor = MockProdutor()

class MockNotaFiscal:
    def __init__(self):
        self.propriedade = MockPropriedade()
        self.numero = 1
        self.serie = '1'
        self.data_emissao = timezone.now().date()
        self.valor_total = Decimal('100.00')
        self.tipo = 'SAIDA'

nota_mock = MockNotaFiscal()

print('Testando emissão de NF-e com mock...')
resultado = emitir_nfe(nota_mock)
print(f'Resultado: {resultado}')

if resultado.get('sucesso'):
    print('✓ Emissão simulada com sucesso!')
    print(f'Chave de acesso: {resultado.get("chave_acesso", "N/A")}')
    print(f'Demo: {resultado.get("demo", False)}')
else:
    print(f'✗ Erro: {resultado.get("erro", "Erro desconhecido")}')