# Script para verificar status das migrations 0071-0074

Write-Host "🔍 Verificando Status das Migrations 0071-0074" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# 1. Verificar status das migrations
Write-Host "`n📊 Status das Migrations:" -ForegroundColor Yellow
python manage.py showmigrations gestao_rural | Select-String -Pattern "007[0-9]|008[0-2]" -Context 0,0

# 2. Verificar se tabelas existem
Write-Host "`n📋 Verificando Tabelas:" -ForegroundColor Yellow
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Verificar tabelas relacionadas
tabelas = ['gestao_rural_produto', 'gestao_rural_categoriaproduto']
for tabela in tabelas:
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='\" + tabela + \"'\")
    existe = cursor.fetchone()
    if existe:
        print(f'✅ {tabela} existe')
    else:
        print(f'❌ {tabela} NÃO existe')
" 2>&1

# 3. Verificar estrutura da tabela Produto
Write-Host "`n🔧 Verificando Estrutura da Tabela Produto:" -ForegroundColor Yellow
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

try:
    cursor.execute('PRAGMA table_info(gestao_rural_produto)')
    cols = cursor.fetchall()
    
    print('Campos importantes:')
    campos_importantes = ['ncm', 'origem_mercadoria', 'cest', 'gtin', 'ex_tipi']
    for col in cols:
        nome = col[1]
        permite_null = col[3] == 0  # 0 = NOT NULL, 1 = NULL permitido
        tipo = col[2]
        
        if any(campo in nome.lower() for campo in campos_importantes):
            status = '❌ Permite NULL' if permite_null else '✅ NOT NULL'
            print(f'  {nome}: {tipo} - {status}')
except Exception as e:
    print(f'❌ Erro: {e}')
    print('   Tabela pode não existir ainda')
" 2>&1

# 4. Verificar modelo Python
Write-Host "`n🐍 Verificando Modelo Python:" -ForegroundColor Yellow
python manage.py shell -c "
try:
    from gestao_rural.models_compras_financeiro import Produto, CategoriaProduto
    
    print('✅ Modelos importados com sucesso')
    print(f'   Produtos no banco: {Produto.objects.count()}')
    print(f'   Categorias no banco: {CategoriaProduto.objects.count()}')
    
    # Verificar produtos sem NCM
    produtos_sem_ncm = Produto.objects.filter(ncm__isnull=True) | Produto.objects.filter(ncm='')
    count_sem_ncm = produtos_sem_ncm.count()
    
    if count_sem_ncm > 0:
        print(f'⚠️  {count_sem_ncm} produto(s) sem NCM encontrado(s)')
        print('   Esses produtos precisam ser corrigidos!')
    else:
        print('✅ Todos os produtos têm NCM configurado')
        
    # Verificar campo NCM no modelo
    campo_ncm = Produto._meta.get_field('ncm')
    if campo_ncm.null:
        print('⚠️  Campo NCM permite NULL no modelo Python')
        print('   Isso pode causar problemas!')
    else:
        print('✅ Campo NCM é obrigatório no modelo Python')
        
except Exception as e:
    print(f'❌ Erro ao verificar modelos: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

# 5. Verificar se há plan de migrations pendentes
Write-Host "`n📦 Migrations Pendentes:" -ForegroundColor Yellow
$plan = python manage.py migrate --plan 2>&1 | Select-String -Pattern "0071|0072|0073|0074" -Context 1,1

if ($plan) {
    Write-Host $plan -ForegroundColor Yellow
} else {
    Write-Host "✅ Nenhuma migration 0071-0074 pendente" -ForegroundColor Green
}

# Resumo
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ Verificação concluída!" -ForegroundColor Green
Write-Host "`n💡 Próximos passos:" -ForegroundColor Cyan
Write-Host "   - Se migrations não foram aplicadas: python manage.py migrate gestao_rural 0071" -ForegroundColor White
Write-Host "   - Se há produtos sem NCM: Corrigir manualmente ou usar migration de correção" -ForegroundColor White
Write-Host "   - Se campo NCM permite NULL: Aplicar migration 0072 corrigida" -ForegroundColor White






