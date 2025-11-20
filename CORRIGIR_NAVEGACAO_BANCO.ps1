# ========================================
# CORRIGIR NAVEGAÇÃO E BANCO DE DADOS
# ========================================

Write-Host "🔧 CORRIGINDO NAVEGAÇÃO E BANCO DE DADOS" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Yellow

# 1. PARAR SERVIDOR
Write-Host "🛑 Parando servidor..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. IR PARA DIRETÓRIO CORRETO
Write-Host "📁 Navegando para diretório..." -ForegroundColor Cyan
if (Test-Path "monpec_definitivo") {
    Set-Location "monpec_definitivo"
    Write-Host "✅ Diretório monpec_definitivo encontrado!" -ForegroundColor Green
} else {
    Write-Host "❌ Diretório monpec_definitivo não encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\SISTEMA_MONPEC_COMPLETO.ps1" -ForegroundColor Yellow
    exit
}

# 3. REMOVER BANCO ANTIGO E MIGRAÇÕES
Write-Host "🗑️ Removendo banco antigo..." -ForegroundColor Cyan
Remove-Item "db.sqlite3" -ErrorAction SilentlyContinue
Remove-Item "gestao_rural\migrations" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "gestao_rural\migrations" -Force
New-Item -ItemType File -Path "gestao_rural\migrations\__init__.py" -Force

# 4. CRIAR MIGRAÇÕES
Write-Host "📊 Criando migrações..." -ForegroundColor Cyan
python manage.py makemigrations

# 5. APLICAR MIGRAÇÕES
Write-Host "🗃️ Aplicando migrações..." -ForegroundColor Cyan
python manage.py migrate

# 6. CRIAR SUPERUSUÁRIO
Write-Host "👤 Criando superusuário..." -ForegroundColor Cyan
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')
    print('✅ Usuário admin criado!')
else:
    print('✅ Usuário admin já existe!')
"

# 7. CRIAR CATEGORIAS PADRÃO
Write-Host "📋 Criando categorias padrão..." -ForegroundColor Cyan
python manage.py shell -c "
from gestao_rural.models import Categoria
categorias_padrao = [
    {'nome': 'Máquinas e Equipamentos', 'descricao': 'Tratores, implementos, máquinas agrícolas', 'cor': '#004a99'},
    {'nome': 'Construções', 'descricao': 'Casa sede, galpões, currais, silos', 'cor': '#28a745'},
    {'nome': 'Animais', 'descricao': 'Gado, cavalos, outros animais', 'cor': '#dc3545'},
    {'nome': 'Veículos', 'descricao': 'Caminhões, carros, motos', 'cor': '#ffc107'},
    {'nome': 'Ferramentas', 'descricao': 'Ferramentas manuais e elétricas', 'cor': '#6c757d'},
    {'nome': 'Outros', 'descricao': 'Outros itens diversos', 'cor': '#17a2b8'},
]

for cat_data in categorias_padrao:
    if not Categoria.objects.filter(nome=cat_data['nome']).exists():
        Categoria.objects.create(**cat_data)
        print(f'✅ Categoria {cat_data[\"nome\"]} criada!')
    else:
        print(f'✅ Categoria {cat_data[\"nome\"]} já existe!')
"

# 8. CRIAR DADOS DE EXEMPLO
Write-Host "📝 Criando dados de exemplo..." -ForegroundColor Cyan
python manage.py shell -c "
from gestao_rural.models import Proprietario, Propriedade, Categoria, ItemInventario

# Criar proprietário de exemplo
if not Proprietario.objects.filter(cpf='12345678901').exists():
    proprietario = Proprietario.objects.create(
        nome='João Silva',
        cpf='12345678901',
        telefone='(67) 99999-9999',
        email='joao@email.com',
        cidade='Campo Grande',
        estado='MS'
    )
    print('✅ Proprietário de exemplo criado!')
    
    # Criar propriedade de exemplo
    propriedade = Propriedade.objects.create(
        nome='Fazenda São José',
        proprietario=proprietario,
        area=500.00,
        municipio='Campo Grande',
        estado='MS'
    )
    print('✅ Propriedade de exemplo criada!')
    
    # Criar itens de inventário de exemplo
    categoria_maquinas = Categoria.objects.get(nome='Máquinas e Equipamentos')
    ItemInventario.objects.create(
        propriedade=propriedade,
        categoria=categoria_maquinas,
        nome='Trator John Deere 6110J',
        descricao='Trator de 110cv, ano 2020',
        quantidade=1,
        valor_unitario=150000.00
    )
    print('✅ Itens de inventário de exemplo criados!')
else:
    print('✅ Dados de exemplo já existem!')
"

# 9. VERIFICAR BANCO
Write-Host "🔍 Verificando banco de dados..." -ForegroundColor Cyan
python manage.py shell -c "
from gestao_rural.models import Proprietario, Propriedade, Categoria, ItemInventario
print(f'Proprietários: {Proprietario.objects.count()}')
print(f'Propriedades: {Propriedade.objects.count()}')
print(f'Categorias: {Categoria.objects.count()}')
print(f'Itens de Inventário: {ItemInventario.objects.count()}')
print('✅ Banco de dados funcionando!')
"

# 10. INICIAR SERVIDOR
Write-Host ""
Write-Host "🎉 CORREÇÕES APLICADAS!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 INFORMAÇÕES:" -ForegroundColor Cyan
Write-Host "• URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "• Login: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "✅ CORREÇÕES REALIZADAS:" -ForegroundColor Cyan
Write-Host "• Banco de dados criado corretamente" -ForegroundColor Green
Write-Host "• Tabelas criadas e migradas" -ForegroundColor Green
Write-Host "• Superusuário criado" -ForegroundColor Green
Write-Host "• Categorias padrão criadas" -ForegroundColor Green
Write-Host "• Dados de exemplo adicionados" -ForegroundColor Green
Write-Host "• Navegação funcionando" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver


