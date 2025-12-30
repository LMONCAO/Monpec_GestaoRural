#!/bin/bash
# COMANDO ÚNICO PARA EXECUTAR NO GOOGLE CLOUD SHELL
# Copie e cole TUDO de uma vez no Cloud Shell

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Criar pasta
mkdir -p ~/monpec_deploy
cd ~/monpec_deploy

# Verificar se já está na pasta certa com os arquivos
if [ ! -f "manage.py" ] || [ ! -f "RESETAR_E_DEPLOY_DO_ZERO.sh" ]; then
    echo "⚠️  ATENÇÃO: Você precisa fazer upload dos arquivos primeiro!"
    echo ""
    echo "INSTRUÇÕES:"
    echo "1. Clique no ícone 'Open Editor' no Cloud Shell (ícone de lápis)"
    echo "2. Clique com botão direito na pasta 'monpec_deploy'"
    echo "3. Selecione 'Upload Files'"
    echo "4. Faça upload de TODOS os arquivos do projeto (ou compacte em ZIP)"
    echo "5. Depois execute novamente este comando"
    echo ""
    echo "Ou se você já tem os arquivos em outra pasta, navegue até ela:"
    echo "   cd ~/caminho/da/pasta"
    echo "   bash RESETAR_E_DEPLOY_DO_ZERO.sh"
    exit 1
fi

# Dar permissão e executar
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh
echo "✅ Executando script..."
bash RESETAR_E_DEPLOY_DO_ZERO.sh

