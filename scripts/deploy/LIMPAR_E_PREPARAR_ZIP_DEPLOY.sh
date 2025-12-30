#!/bin/bash
# Script Bash para limpar e criar ZIP apenas com arquivos necessários para deploy
# Execute: bash LIMPAR_E_PREPARAR_ZIP_DEPLOY.sh

echo "🧹 Limpando e preparando arquivos para deploy..."
echo ""

# Criar pasta temporária limpa
PASTA_LIMPA="Monpec_GestaoRural_LIMPO"
ZIP_FINAL="Monpec_Deploy.zip"

# Remover pasta e ZIP anteriores se existirem
if [ -d "$PASTA_LIMPA" ]; then
    rm -rf "$PASTA_LIMPA"
    echo "✅ Pasta anterior removida"
fi

if [ -f "$ZIP_FINAL" ]; then
    rm -f "$ZIP_FINAL"
    echo "✅ ZIP anterior removido"
fi

# Criar pasta limpa
mkdir -p "$PASTA_LIMPA"
echo "✅ Pasta limpa criada: $PASTA_LIMPA"
echo ""

echo "📋 Copiando arquivos essenciais..."

# Arquivos essenciais
ARQUIVOS_ESSENCIAIS=(
    "manage.py"
    "Dockerfile.prod"
    "requirements_producao.txt"
    "app.yaml"
    "cloudbuild.yaml"
    "RESETAR_E_DEPLOY_DO_ZERO.sh"
    "README.md"
)

for arquivo in "${ARQUIVOS_ESSENCIAIS[@]}"; do
    if [ -f "$arquivo" ]; then
        cp "$arquivo" "$PASTA_LIMPA/"
        echo "  ✅ $arquivo"
    else
        echo "  ⚠️  $arquivo não encontrado (pode ser opcional)"
    fi
done

echo ""
echo "📁 Copiando pastas essenciais..."

# Pastas essenciais
PASTAS_ESSENCIAIS=(
    "sistema_rural"
    "gestao_rural"
    "templates"
    "static"
    "api"
    "scripts"
)

for pasta in "${PASTAS_ESSENCIAIS[@]}"; do
    if [ -d "$pasta" ]; then
        cp -r "$pasta" "$PASTA_LIMPA/"
        echo "  ✅ $pasta/"
    else
        echo "  ⚠️  $pasta/ não encontrada (pode ser opcional)"
    fi
done

# Verificar se manage.py foi copiado (essencial)
if [ ! -f "$PASTA_LIMPA/manage.py" ]; then
    echo ""
    echo "❌ ERRO: manage.py não encontrado! O deploy não funcionará sem ele."
    exit 1
fi

echo ""
echo "🗜️  Criando ZIP..."

# Criar ZIP
cd "$PASTA_LIMPA"
zip -r "../$ZIP_FINAL" . -q
cd ..

echo ""
echo "✅ ZIP criado com sucesso: $ZIP_FINAL"
echo ""

# Calcular tamanho
if command -v du &> /dev/null; then
    TAMANHO=$(du -h "$ZIP_FINAL" | cut -f1)
    echo "📊 Tamanho do ZIP: $TAMANHO"
fi

echo ""
echo "🎉 PRONTO! Arquivo $ZIP_FINAL está pronto para upload no Cloud Shell!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Faça upload do arquivo $ZIP_FINAL no Google Cloud Shell"
echo "2. Descompacte: unzip $ZIP_FINAL"
echo "3. Execute: bash RESETAR_E_DEPLOY_DO_ZERO.sh"
echo ""

# Perguntar se quer limpar a pasta temporária
read -p "Deseja remover a pasta temporária $PASTA_LIMPA? (s/N): " resposta
if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    rm -rf "$PASTA_LIMPA"
    echo "✅ Pasta temporária removida"
fi

echo ""
echo "✅ Concluído!"

