#!/bin/bash
# Script para gerar requirements.txt a partir do ambiente atual
# Execute no ambiente onde o sistema está funcionando corretamente

echo "Gerando requirements.txt a partir do ambiente atual..."
echo ""

# Gerar requirements.txt
pip freeze > requirements.txt

# Adicionar comentário no início
cat > requirements_temp.txt << 'EOF'
# Requirements gerado automaticamente a partir do ambiente de desenvolvimento
# Este arquivo contém todas as dependências necessárias para o sistema MONPEC
#
# Para gerar novamente, execute: pip freeze > requirements.txt
# Para instalar: pip install -r requirements.txt

EOF

# Adicionar requirements congelados
cat requirements.txt >> requirements_temp.txt
mv requirements_temp.txt requirements.txt

echo "✓ requirements.txt gerado com sucesso!"
echo ""
echo "Agora você pode copiar este arquivo para requirements_producao.txt se necessário:"
echo "  cp requirements.txt requirements_producao.txt"
echo ""





