#!/bin/bash
# ========================================
# SETUP VERSÃO DE DEMONSTRAÇÃO - MONPEC
# ========================================

echo ""
echo "🎯 CONFIGURANDO VERSÃO DE DEMONSTRAÇÃO"
echo "====================================="
echo ""

# 1. Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ ERRO: Arquivo manage.py não encontrado!"
    echo "   Execute este script no diretório raiz do projeto."
    exit 1
fi

# 0. BACKUP AUTOMÁTICO ANTES DE CONFIGURAR DEMO
echo "🔒 Fazendo backup automático do sistema..."
echo "   (Isso garante que seus dados estão seguros)"

if [ -f "./backup_antes_demo.sh" ]; then
    chmod +x ./backup_antes_demo.sh
    ./backup_antes_demo.sh
    echo ""
    echo "✅ Backup concluído! Continuando com setup da demo..."
    echo ""
else
    echo "⚠️  Script de backup não encontrado, mas continuando..."
    echo "   Recomendado: Execute ./backup_antes_demo.sh manualmente antes"
    echo ""
    read -p "   Continuar mesmo assim? (S/N): " continuar
    if [ "$continuar" != "S" ] && [ "$continuar" != "s" ]; then
        echo "   Setup cancelado pelo usuário."
        exit 0
    fi
    echo ""
fi

# 2. Executar migrações
echo "📦 Executando migrações do banco de dados..."
python manage.py makemigrations
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ ERRO ao executar migrações!"
    exit 1
fi
echo "✅ Migrações executadas com sucesso!"

# 3. Criar usuário demo
echo ""
echo "👤 Criando usuário de demonstração..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123')
    user.first_name = 'Usuário'
    user.last_name = 'Demonstração'
    user.save()
    print('✅ Usuário demo criado com sucesso!')
    print('   Username: demo')
    print('   Senha: demo123')
else:
    print('ℹ️ Usuário demo já existe')
    user = User.objects.get(username='demo')
    user.set_password('demo123')
    user.save()
    print('✅ Senha do usuário demo atualizada!')
EOF

# 4. Popular dados de demonstração (SEGURANÇA: Usa get_or_create, não sobrescreve)
echo ""
echo "📊 Populando dados de demonstração..."
echo "   ℹ️  Os dados serão ADICIONADOS, não substituirão dados existentes!"
echo "   ℹ️  O script usa get_or_create, então é seguro executar múltiplas vezes"
if [ -f "populate_test_data.py" ]; then
    python populate_test_data.py
    if [ $? -eq 0 ]; then
        echo "✅ Dados de demonstração criados com sucesso!"
    else
        echo "⚠️ Aviso: Alguns dados podem já existir (isso é normal)"
    fi
else
    echo "⚠️ Arquivo populate_test_data.py não encontrado"
    echo "   Pulando população de dados..."
fi

# 5. Mensagem final
echo ""
echo "====================================="
echo "✅ VERSÃO DE DEMONSTRAÇÃO CONFIGURADA!"
echo "====================================="
echo ""
echo "📋 CREDENCIAIS DE ACESSO:"
echo "   URL: http://localhost:8000"
echo "   Usuário: demo"
echo "   Senha: demo123"
echo ""
echo "📊 DADOS DE DEMONSTRAÇÃO:"
echo "   • Produtor: João Silva"
echo "   • Propriedade: Fazenda São José"
echo "   • Localização: Ribeirão Preto - SP"
echo "   • Área: 500 hectares"
echo ""
echo "🚀 PARA INICIAR O SERVIDOR:"
echo "   python manage.py runserver"
echo ""
echo "🌐 PARA ACESSO REMOTO (rede local):"
echo "   python manage.py runserver 0.0.0.0:8000"
echo "   Depois acesse: http://[SEU_IP]:8000"
echo ""
echo "💡 DICA: Para resetar os dados de demo, execute:"
echo "   python manage.py flush --no-input"
echo "   Depois execute este script novamente."
echo ""
echo "🔒 SEGURANÇA:"
echo "   • Seus dados originais estão seguros no backup"
echo "   • Os dados de demo foram ADICIONADOS, não substituídos"
echo "   • Para restaurar: Use o backup em ./backups/backup_antes_demo_*"
echo ""

# 6. Perguntar se deseja iniciar o servidor
read -p "Deseja iniciar o servidor agora? (S/N): " iniciar
if [ "$iniciar" = "S" ] || [ "$iniciar" = "s" ] || [ "$iniciar" = "Y" ] || [ "$iniciar" = "y" ]; then
    echo ""
    echo "🚀 Iniciando servidor Django..."
    echo "   Pressione Ctrl+C para parar"
    echo ""
    python manage.py runserver
fi

