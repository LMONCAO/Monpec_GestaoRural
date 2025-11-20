#!/bin/bash
# ========================================
# BACKUP SEGURO ANTES DE CONFIGURAR DEMO
# ========================================

echo ""
echo "🔒 CRIANDO BACKUP SEGURO DO SISTEMA"
echo "==================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ ERRO: Arquivo manage.py não encontrado!"
    echo "   Execute este script no diretório raiz do projeto."
    exit 1
fi

# Obter data e hora para nome do backup
dataBackup=$(date +"%Y-%m-%d_%H-%M-%S")
nomeBackup="backup_antes_demo_$dataBackup"
pastaBackup="./backups/$nomeBackup"

echo "📁 Criando pasta de backup: $pastaBackup"
mkdir -p "$pastaBackup/banco_dados"
mkdir -p "$pastaBackup/codigo_fonte"
mkdir -p "$pastaBackup/configuracoes"

# 1. BACKUP DO BANCO DE DADOS (CRÍTICO)
echo ""
echo "💾 1. Fazendo backup do banco de dados..."

if [ -f "./db.sqlite3" ]; then
    # Verificar processos Python
    if pgrep -x "python" > /dev/null; then
        echo "   ⚠️  ATENÇÃO: Processos Python detectados!"
        echo "   Recomendado: Pare o servidor Django antes do backup"
        read -p "   Continuar mesmo assim? (S/N): " continuar
        if [ "$continuar" != "S" ] && [ "$continuar" != "s" ]; then
            echo "   Backup cancelado pelo usuário."
            exit 0
        fi
    fi
    
    # Copiar banco de dados
    cp "./db.sqlite3" "$pastaBackup/banco_dados/db.sqlite3"
    cp "./db.sqlite3-shm" "$pastaBackup/banco_dados/db.sqlite3-shm" 2>/dev/null
    cp "./db.sqlite3-wal" "$pastaBackup/banco_dados/db.sqlite3-wal" 2>/dev/null
    
    # Verificar tamanho
    tamanhoBanco=$(stat -f%z "$pastaBackup/banco_dados/db.sqlite3" 2>/dev/null || stat -c%s "$pastaBackup/banco_dados/db.sqlite3" 2>/dev/null)
    tamanhoMB=$(echo "scale=2; $tamanhoBanco / 1024 / 1024" | bc)
    echo "   ✅ Banco de dados copiado (${tamanhoMB} MB)"
else
    echo "   ⚠️  Banco de dados não encontrado (db.sqlite3)"
fi

# 2. BACKUP DE CONFIGURAÇÕES
echo ""
echo "⚙️  2. Fazendo backup de configurações..."

if [ -f "sistema_rural/settings.py" ]; then
    cp "sistema_rural/settings.py" "$pastaBackup/configuracoes/settings.py"
fi
if [ -f "sistema_rural/urls.py" ]; then
    cp "sistema_rural/urls.py" "$pastaBackup/configuracoes/urls.py"
fi
if [ -f "manage.py" ]; then
    cp "manage.py" "$pastaBackup/configuracoes/manage.py"
fi
if [ -f "requirements.txt" ]; then
    cp "requirements.txt" "$pastaBackup/configuracoes/requirements.txt"
fi

echo "   ✅ Configurações copiadas"

# 3. BACKUP DE SCRIPTS DE DEMO
echo ""
echo "📝 3. Salvando scripts de demo..."
if [ -f "./setup_demo.sh" ]; then
    cp "./setup_demo.sh" "$pastaBackup/configuracoes/setup_demo.sh"
fi
if [ -f "./populate_test_data.py" ]; then
    cp "./populate_test_data.py" "$pastaBackup/configuracoes/populate_test_data.py"
fi
echo "   ✅ Scripts salvos"

# 4. Criar arquivo de informações
echo ""
echo "📋 4. Criando arquivo de informações..."

cat > "$pastaBackup/INFO_BACKUP.txt" << EOF
=== BACKUP ANTES DE CONFIGURAR DEMO ===
Data/Hora: $dataBackup
Nome: $nomeBackup

=== CONTEÚDO DO BACKUP ===
- Banco de dados SQLite completo (db.sqlite3)
- Arquivos de configuração do Django
- Scripts de demo (para referência)

=== IMPORTANTE ===
Este backup foi criado ANTES de configurar a versão de demonstração.
Se algo der errado, você pode restaurar usando este backup.

=== RESTAURAÇÃO ===
Para restaurar este backup:

1. PARAR o servidor Django (se estiver rodando)
2. Copiar o banco de dados de volta:
   cp "./backups/$nomeBackup/banco_dados/db.sqlite3" "./db.sqlite3"
   cp "./backups/$nomeBackup/banco_dados/db.sqlite3-shm" "./db.sqlite3-shm"
   cp "./backups/$nomeBackup/banco_dados/db.sqlite3-wal" "./db.sqlite3-wal"

3. Verificar se está funcionando:
   python manage.py migrate
   python manage.py runserver

=== SEGURANÇA ===
- Este backup contém TODOS os seus dados atuais
- Mantenha este backup seguro
- Não compartilhe este backup com ninguém
- O backup está localizado em: $pastaBackup

=== PRÓXIMOS PASSOS ===
Agora você pode executar: ./setup_demo.sh
Os dados de demo serão ADICIONADOS ao banco, não substituirão dados existentes.
EOF

echo "   ✅ Arquivo de informações criado"

# 5. Calcular tamanho
echo ""
echo "📊 Calculando tamanho do backup..."
tamanhoTotal=$(du -sb "$pastaBackup" 2>/dev/null | cut -f1)
tamanhoMB=$(echo "scale=2; $tamanhoTotal / 1024 / 1024" | bc)

# 6. Resumo final
echo ""
echo "==================================="
echo "✅ BACKUP CONCLUÍDO COM SUCESSO!"
echo "==================================="
echo ""
echo "📁 Localização: $pastaBackup"
echo "📦 Tamanho: ${tamanhoMB} MB"
echo ""
echo "🔒 SEU SISTEMA ESTÁ PROTEGIDO!"
echo ""
echo "✅ Agora você pode executar:"
echo "   ./setup_demo.sh"
echo ""
echo "💡 Os dados de demo serão ADICIONADOS, não substituirão seus dados!"
echo ""





