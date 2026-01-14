import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, ProdutorRural
from gestao_rural.services_nfe import emitir_nfe
from django.utils import timezone
from decimal import Decimal

# Criar uma nota fiscal de teste
class NotaFiscalTeste:
    def __init__(self, propriedade):
        self.propriedade = propriedade
        self.numero = 1
        self.serie = '1'
        self.data_emissao = timezone.now().date()
        self.valor_total = Decimal('100.00')
        self.tipo = 'SAIDA'
        self.cliente = None  # Para teste simplificado

    @property
    def cnpj(self):
        # Propriedade não tem cnpj diretamente, buscar do produtor
        if hasattr(self.propriedade, 'produtor') and self.propriedade.produtor:
            return self.propriedade.produtor.cpf_cnpj
        return '00000000000000'

print("=== TESTE DE EMISSÃO REAL DE NF-e ===")

# 1. Verificar propriedades disponíveis
propriedades = Propriedade.objects.all()
print(f"Propriedades encontradas: {propriedades.count()}")

if propriedades.exists():
    propriedade = propriedades.first()
    print(f"Usando propriedade: {propriedade.nome_propriedade}")

    # 2. Verificar certificado do produtor
    produtor = propriedade.produtor
    if produtor:
        print(f"\\nProdutor: {produtor.nome}")
        print(f"Tipo de certificado: {produtor.certificado_tipo}")
        print(f"Thumbprint: {produtor.certificado_thumbprint or 'N/A'}")
        print(f"Tem certificado válido: {produtor.tem_certificado_valido()}")

        # 3. Testar emissão
        nota_teste = NotaFiscalTeste(propriedade)
        print(f"\\nTestando emissão de NF-e...")

        try:
            resultado = emitir_nfe(nota_teste)
            print(f"\\nResultado da emissão:")
            print(f"Sucesso: {resultado.get('sucesso', False)}")

            if resultado.get('sucesso'):
                print(f"Chave de acesso: {resultado.get('chave_acesso', 'N/A')}")
                print(f"Protocolo: {resultado.get('protocolo', 'N/A')}")
                print(f"Método: {resultado.get('metodo', 'N/A')}")
                print(f"Demo: {resultado.get('demo', False)}")

                if resultado.get('demo'):
                    print("\\n⚠️  ATENÇÃO: Esta foi uma emissão DEMO, não real!")
                    print("Para emissão real, configure um certificado digital válido.")
                else:
                    print("\\n✅ EMISSÃO REAL DETECTADA!")
                    print("A NF-e foi emitida através da SEFAZ ou API real.")
            else:
                print(f"Erro: {resultado.get('erro', 'Erro desconhecido')}")

        except Exception as e:
            print(f"Erro durante emissão: {str(e)}")

    else:
        print("Erro: Propriedade não tem produtor associado")

else:
    print("Erro: Nenhuma propriedade encontrada")

print("\\n=== INSTRUÇÕES PARA EMISSÃO REAL ===")
print("1. Configure um certificado digital A1 válido no cadastro do produtor")
print("2. Execute este teste novamente")
print("3. Procure por 'Demo: False' no resultado")
print("4. Verifique os logs do Django para confirmação")