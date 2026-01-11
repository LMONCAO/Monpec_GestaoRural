#!/usr/bin/env python3
"""
CORREÇÃO: Extração correta do número de manejo do SISBOV
O manejo deve ser 036724 (6 dígitos), excluindo o dígito verificador
"""

def extrair_manejo_correto(sisbov):
    """
    Extrai o número de manejo correto: posições 9-14 (Python) = 036724
    Equivalente a =EXT.TEXTO(A1;10;6) no Excel
    """
    if len(sisbov) >= 15:
        # Posições 9-14 em Python = caracteres nas posições 9,10,11,12,13,14
        # Isso resulta em "036724" (excluindo o último dígito verificador)
        return sisbov[9:15]
    return None

# Exemplo do usuário
sisbov = "1055005500367242"
print("🐄 CORREÇÃO - EXTRAÇÃO DE MANEJO SISBOV")
print("=" * 50)
print(f"SISBOV completo: {sisbov}")
print(f"Comprimento: {len(sisbov)} dígitos")
print()

print("📊 ANÁLISE DETALHADA:")
print("Posição | Caractere | Inclui no manejo?")
print("--------|-----------|------------------")
for i in range(len(sisbov)):
    incluir = "✅ SIM" if 9 <= i <= 14 else "❌ NÃO"
    print("2d")
print()

print("🎯 MANEJO CORRETO (6 dígitos):")
manejo_correto = extrair_manejo_correto(sisbov)
print(f"Resultado: {manejo_correto}")
print()

print("📋 COMPARAÇÃO - O QUE VOCÊ QUER vs OUTRAS OPÇÕES:")
print(f"✅ Correto (posição 9-14): {sisbov[9:15]} = {manejo_correto}")
print(f"❌ Errado (posição 8-13):  {sisbov[8:14]} = {sisbov[8:14]}")
print()

print("🛠️  FUNÇÃO CORRIGIDA:")
print("""
def extrair_numero_manejo(sisbov):
    '''Extrai manejo correto: 6 dígitos excluindo dígito verificador'''
    if len(sisbov) >= 15:
        return sisbov[9:15]  # Posições 9-14 em Python
    return None

# Equivalente Excel: =EXT.TEXTO(A1;10;6)
# Pois: posição Excel 10 = posição Python 9
""")

print("📚 RESUMO DA CORREÇÃO:")
print("• SISBOV: 1055005500367242")
print("• Manejo: 036724 (6 dígitos)")
print("• Python: sisbov[9:15]")
print("• Excel: =EXT.TEXTO(A1;10;6)")
print("• Exclui: último dígito (verificador)")

print("\n✅ AGORA FUNCIONA CORRETAMENTE!")