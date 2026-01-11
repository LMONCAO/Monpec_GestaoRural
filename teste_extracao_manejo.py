#!/usr/bin/env python3
"""
Demonstração de como extrair número de manejo do SISBOV
Equivalente à fórmula Excel =EXT.TEXTO()
"""

def extrair_manejo_excel(sisbov, posicao_excel, num_caracteres):
    """
    Equivalente à fórmula Excel =EXT.TEXTO()

    Parâmetros:
    - sisbov: string do código SISBOV
    - posicao_excel: posição inicial (começando do 1 como no Excel)
    - num_caracteres: número de caracteres a extrair
    """
    # Converter posição do Excel (base 1) para Python (base 0)
    posicao_python = posicao_excel - 1

    # Extrair os caracteres
    return sisbov[posicao_python:posicao_python + num_caracteres]

# Exemplo do usuário
sisbov = "1055005500367242"
print("🐄 EXTRAÇÃO DE NÚMERO DE MANEJO - SISBOV")
print("=" * 50)
print(f"SISBOV: {sisbov}")
print(f"Comprimento: {len(sisbov)} dígitos")
print()

print("📊 MAPEAMENTO DAS POSIÇÕES:")
print("Excel | Python | Caractere")
print("------|--------|----------")
for i in range(len(sisbov)):
    print("2d")
print()

# Equivalente à fórmula Excel =EXT.TEXTO(A1;9;6)
print("🎯 FÓRMULA EXCEL =EXT.TEXTO(A1;9;6)")
manejo_excel = extrair_manejo_excel(sisbov, 9, 6)
print(f"Resultado: {manejo_excel}")
print()

# Versões alternativas
print("🔄 VERSÕES ALTERNATIVAS:")
print(f"sisbov[8:14]: {sisbov[8:14]}")  # Posições 8-13 (Python)
print(f"sisbov[9:15]: {sisbov[9:15]}")  # Posições 9-14 (Python)
print()

# Função genérica
print("🛠️  FUNÇÃO GENÉRICA EM PYTHON:")
print("""
def extrair_manejo_excel(texto, posicao_excel, num_caracteres):
    # Excel começa contar do 1, Python do 0
    posicao_python = posicao_excel - 1
    return texto[posicao_python:posicao_python + num_caracteres]

# Uso:
manejo = extrair_manejo_excel("1055005500367242", 9, 6)
""")

# Exemplos práticos
print("📋 EXEMPLOS PRÁTICOS:")
exemplos = [
    "1055005500353825",  # Manejo: 003538
    "1055005500397167",  # Manejo: 003971
    "1055005500318709",  # Manejo: 003187
]

for sisbov_ex in exemplos:
    manejo = extrair_manejo_excel(sisbov_ex, 9, 6)
    print(f"SISBOV: {sisbov_ex} → Manejo: {manejo}")