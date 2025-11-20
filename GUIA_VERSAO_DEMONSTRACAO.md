# 🎯 GUIA COMPLETO - VERSÃO DE DEMONSTRAÇÃO

## 📋 **VISÃO GERAL**

Este guia fornece instruções passo a passo para criar uma versão de demonstração do sistema MONPEC, ideal para apresentações, testes e avaliações por clientes potenciais.

## 🔒 **SEGURANÇA GARANTIDA**

**IMPORTANTE:** A versão de demonstração foi projetada para **NÃO INTERFERIR** no seu sistema em desenvolvimento:

- ✅ **Backup automático** antes de qualquer alteração
- ✅ **Não sobrescreve** dados existentes (usa `get_or_create`)
- ✅ **Não deleta** nada do seu sistema
- ✅ **Apenas adiciona** novos dados de demonstração
- ✅ **Totalmente reversível** a qualquer momento

📖 **Leia o guia completo de segurança:** `GUIA_SEGURANCA_DEMO.md`

---

## 🚀 **OPÇÃO 1: SETUP RÁPIDO (Recomendado)**

> ⚠️ **IMPORTANTE:** O script `setup_demo.ps1` faz backup automático antes de qualquer alteração!

### **Passo 0: Backup Automático (Opcional mas Recomendado)**

Se preferir fazer backup manualmente antes:

```powershell
# Fazer backup manual (opcional)
.\backup_antes_demo.ps1
```

O script `setup_demo.ps1` faz isso automaticamente, mas você pode fazer manualmente se preferir.

### **Passo 1: Preparar o Ambiente**

```bash
# No PowerShell (Windows)
cd C:\Monpec_projetista

# Verificar se o ambiente virtual está ativo
python --version
```

### **Passo 2: Executar Migrações**

```bash
# Criar e aplicar migrações
python manage.py makemigrations
python manage.py migrate
```

### **Passo 3: Criar Usuário de Demonstração**

```bash
# Criar usuário demo com permissões de superusuário
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123')
    print('✅ Usuário demo criado com sucesso!')
else:
    print('ℹ️ Usuário demo já existe')
"
```

### **Passo 4: Popular Dados de Demonstração**

```bash
# Executar script de população de dados
python populate_test_data.py
```

### **Passo 5: Iniciar Servidor**

```bash
# Iniciar servidor Django
python manage.py runserver
```

### **Acesso à Demonstração**

- **URL:** http://localhost:8000
- **Usuário:** `demo`
- **Senha:** `demo123`

### **🔒 Segurança**

- ✅ Backup foi criado automaticamente em `.\backups\backup_antes_demo_*`
- ✅ Seus dados originais estão protegidos
- ✅ Dados de demo foram **ADICIONADOS**, não substituídos

---

## 🔧 **OPÇÃO 2: SETUP COMPLETO COM SCRIPT AUTOMATIZADO**

### **Criar Script de Setup Completo**

Crie um arquivo `setup_demo.ps1` (PowerShell) ou `setup_demo.sh` (Linux/Mac):

#### **Para Windows (PowerShell):**

```powershell
# setup_demo.ps1
Write-Host "🎯 CONFIGURANDO VERSÃO DE DEMONSTRAÇÃO" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow

# 1. Parar processos Python existentes
Write-Host "🛑 Parando processos Python..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Executar migrações
Write-Host "📦 Executando migrações..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

# 3. Criar usuário demo
Write-Host "👤 Criando usuário de demonstração..." -ForegroundColor Cyan
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123')
    user.first_name = 'Usuário'
    user.last_name = 'Demonstração'
    user.save()
    print('✅ Usuário demo criado!')
else:
    print('ℹ️ Usuário demo já existe')
"

# 4. Popular dados de demonstração
Write-Host "📊 Populando dados de demonstração..." -ForegroundColor Cyan
python populate_test_data.py

# 5. Mensagem final
Write-Host ""
Write-Host "✅ VERSÃO DE DEMONSTRAÇÃO CONFIGURADA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 CREDENCIAIS DE ACESSO:" -ForegroundColor Cyan
Write-Host "• URL: http://localhost:8000" -ForegroundColor White
Write-Host "• Usuário: demo" -ForegroundColor White
Write-Host "• Senha: demo123" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para iniciar o servidor:" -ForegroundColor Cyan
Write-Host "python manage.py runserver" -ForegroundColor Yellow
Write-Host ""
```

#### **Para Linux/Mac (Bash):**

```bash
#!/bin/bash
# setup_demo.sh

echo "🎯 CONFIGURANDO VERSÃO DE DEMONSTRAÇÃO"
echo "====================================="

# 1. Executar migrações
echo "📦 Executando migrações..."
python manage.py makemigrations
python manage.py migrate

# 2. Criar usuário demo
echo "👤 Criando usuário de demonstração..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123')
    user.first_name = 'Usuário'
    user.last_name = 'Demonstração'
    user.save()
    print('✅ Usuário demo criado!')
else:
    print('ℹ️ Usuário demo já existe')
EOF

# 3. Popular dados de demonstração
echo "📊 Populando dados de demonstração..."
python populate_test_data.py

# 4. Mensagem final
echo ""
echo "✅ VERSÃO DE DEMONSTRAÇÃO CONFIGURADA!"
echo "====================================="
echo ""
echo "📋 CREDENCIAIS DE ACESSO:"
echo "• URL: http://localhost:8000"
echo "• Usuário: demo"
echo "• Senha: demo123"
echo ""
echo "🚀 Para iniciar o servidor:"
echo "python manage.py runserver"
echo ""
```

### **Executar o Script**

**Windows:**
```powershell
.\setup_demo.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_demo.sh
./setup_demo.sh
```

---

## 📊 **DADOS DE DEMONSTRAÇÃO INCLUÍDOS**

O script `populate_test_data.py` cria automaticamente:

### **1. Usuário de Teste**
- **Username:** `teste`
- **Email:** `teste@exemplo.com`
- **Senha:** `123456`

### **2. Produtor Rural**
- **Nome:** João Silva
- **CPF:** 12345678901
- **Experiência:** 15 anos

### **3. Propriedade**
- **Nome:** Fazenda São José
- **Localização:** Ribeirão Preto - SP
- **Área:** 500 hectares
- **Tipo:** Mista (Pecuária + Agricultura)
- **Ciclo:** Completo

### **4. Inventário de Rebanho**
- Categorias completas (Vacas, Touros, Bezerras, Bezerros, Novilhas, Novilhos)
- Quantidades aleatórias por categoria
- Valores por cabeça configurados

### **5. Parâmetros de Projeção**
- Taxa de natalidade: 85%
- Taxa de mortalidade adultos: 3%
- Taxa de mortalidade bezerros: 8%
- Taxa de descarte: 15%
- Preço médio de venda: R$ 180,00/@

### **6. Custos**
- **Fixos:** Mão de obra, aluguel, energia, combustível, manutenção
- **Variáveis:** Ração, medicamentos, sementes, inseminação

### **7. Financiamentos**
- Financiamento Rural - Banco do Brasil (R$ 150.000)
- Empréstimo Pessoal - Caixa (R$ 50.000)

### **8. Bens Patrimoniais**
- Trator John Deere
- Cerca elétrica
- Curral de manejo
- Caminhão Ford Cargo

### **9. Projetos Bancários**
- Expansão do Rebanho (Em análise)
- Modernização da Infraestrutura (Aprovado)

### **10. Indicadores Financeiros**
- Receita Bruta Anual
- Custos Operacionais
- Lucro Líquido
- Margem de Lucro
- ROI

---

## 🎨 **PERSONALIZAÇÃO DA DEMONSTRAÇÃO**

### **Criar Dados Mais Realistas**

Você pode modificar o arquivo `populate_test_data.py` para criar dados mais específicos:

```python
# Exemplo: Criar múltiplas propriedades
propriedades_data = [
    {
        'nome': 'Fazenda São José',
        'municipio': 'Ribeirão Preto',
        'uf': 'SP',
        'area': 500,
        'tipo': 'PECUARIA',
        'ciclo': 'CICLO_COMPLETO'
    },
    {
        'nome': 'Fazenda Boa Vista',
        'municipio': 'Dourados',
        'uf': 'MS',
        'area': 800,
        'tipo': 'AGRICULTURA',
        'ciclo': None
    }
]
```

### **Adicionar Mais Usuários Demo**

```python
# Criar múltiplos usuários para demonstração
usuarios_demo = [
    {'username': 'demo_admin', 'email': 'admin@demo.com', 'senha': 'demo123'},
    {'username': 'demo_user', 'email': 'user@demo.com', 'senha': 'demo123'},
]
```

---

## 🔒 **CONFIGURAÇÕES DE SEGURANÇA PARA DEMO**

### **1. Criar Settings Específico para Demo**

Crie um arquivo `sistema_rural/settings_demo.py`:

```python
from .settings import *

# Configurações específicas para demonstração
DEBUG = True
ALLOWED_HOSTS = ['*']  # Permitir acesso de qualquer IP

# Desabilitar algumas funcionalidades sensíveis
# (se necessário)

# Mensagem de aviso no topo
DEMO_MODE = True
DEMO_MESSAGE = "⚠️ MODO DEMONSTRAÇÃO - Dados são apenas para teste"
```

### **2. Adicionar Banner de Demo**

No template base, adicione um banner informativo:

```html
{% if DEMO_MODE %}
<div class="alert alert-warning alert-dismissible fade show" role="alert">
    <strong>⚠️ MODO DEMONSTRAÇÃO</strong> - Este é um ambiente de teste. 
    Os dados são fictícios e apenas para demonstração.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endif %}
```

---

## 📱 **ACESSO REMOTO PARA DEMONSTRAÇÃO**

### **Configurar para Acesso na Rede Local**

1. **Atualizar ALLOWED_HOSTS:**

```python
# sistema_rural/settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.XXX',  # Seu IP na rede local
    '0.0.0.0',
]
```

2. **Iniciar Servidor com IP:**

```bash
# Permitir acesso de qualquer IP na rede local
python manage.py runserver 0.0.0.0:8000
```

3. **Acessar de Outros Dispositivos:**

- **No computador:** http://localhost:8000
- **No celular/tablet:** http://192.168.1.XXX:8000 (substitua pelo IP do seu PC)

---

## 🌐 **DEPLOY PARA DEMONSTRAÇÃO ONLINE**

### **Opção 1: Google Cloud Platform**

```bash
# Usar o script de deploy existente
.\deploy_google_cloud.ps1
```

### **Opção 2: Servidor Temporário**

Para uma demonstração temporária, você pode usar:

- **Heroku** (gratuito com limitações)
- **Railway** (gratuito)
- **Render** (gratuito)

---

## 📋 **CHECKLIST DE DEMONSTRAÇÃO**

Antes de apresentar, verifique:

- [ ] Usuário demo criado e funcionando
- [ ] Dados de demonstração populados
- [ ] Todas as funcionalidades principais testadas
- [ ] Projeções de rebanho funcionando
- [ ] Relatórios gerando corretamente
- [ ] Dashboard carregando sem erros
- [ ] Acesso funcionando (local ou remoto)
- [ ] Banner de modo demo visível (se aplicável)

---

## 🎯 **ROTEIRO DE APRESENTAÇÃO SUGERIDO**

### **1. Login e Dashboard (2 min)**
- Mostrar login com usuário demo
- Apresentar dashboard principal
- Explicar visão geral do sistema

### **2. Gestão de Propriedades (3 min)**
- Mostrar cadastro de produtor
- Exibir propriedades cadastradas
- Explicar tipos de operação

### **3. Módulo Pecuária (5 min)**
- Inventário de rebanho
- Parâmetros de projeção
- Projeção 5 anos
- Gráficos e análises

### **4. Módulo Financeiro (3 min)**
- Custos fixos e variáveis
- Financiamentos
- Indicadores financeiros

### **5. Projetos Bancários (3 min)**
- Criar projeto de exemplo
- Mostrar análise de viabilidade
- Exibir relatórios

### **6. Relatórios (2 min)**
- Gerar relatório PDF
- Mostrar exportações
- Explicar formatação profissional

**Tempo Total:** ~18 minutos + tempo para perguntas

---

## 🔄 **RESETAR DADOS DE DEMONSTRAÇÃO**

### **⚠️ ATENÇÃO: Isso vai deletar TODOS os dados, incluindo os seus!**

Se precisar resetar os dados:

```bash
# Opção 1: Limpar banco e recriar (DELETA TUDO!)
python manage.py flush --no-input
python manage.py migrate
python populate_test_data.py
```

### **Opção 2: Remover Apenas Dados de Demo (Recomendado)**

```python
# No shell do Django:
python manage.py shell

from django.contrib.auth.models import User
from gestao_rural.models import *

# Remover apenas dados de demo
User.objects.filter(username='demo').delete()
ProdutorRural.objects.filter(cpf_cnpj='12345678901').delete()
Propriedade.objects.filter(nome_propriedade='Fazenda São José').delete()

print('✅ Apenas dados de demo foram removidos!')
```

### **Opção 3: Restaurar do Backup (Mais Seguro)**

```powershell
# 1. Parar servidor
Get-Process python | Stop-Process -Force

# 2. Encontrar backup mais recente
$backup = Get-ChildItem ".\backups\backup_antes_demo_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# 3. Restaurar banco de dados
Copy-Item "$backup\banco_dados\db.sqlite3" -Destination ".\db.sqlite3" -Force
Copy-Item "$backup\banco_dados\db.sqlite3-shm" -Destination ".\db.sqlite3-shm" -Force -ErrorAction SilentlyContinue
Copy-Item "$backup\banco_dados\db.sqlite3-wal" -Destination ".\db.sqlite3-wal" -Force -ErrorAction SilentlyContinue

# 4. Verificar
python manage.py migrate
python manage.py runserver
```

---

## 📞 **SUPORTE E DÚVIDAS**

Para dúvidas ou problemas:

1. Verificar logs do Django: `django_error.log`
2. Verificar console do navegador (F12)
3. Executar em modo debug: `DEBUG = True` em settings.py

---

## ✅ **RESUMO RÁPIDO**

### **Método Automático (Recomendado):**

```powershell
# Executa tudo automaticamente, incluindo backup!
.\setup_demo.ps1
```

### **Método Manual:**

```bash
# 1. Backup (IMPORTANTE!)
.\backup_antes_demo.ps1

# 2. Migrações
python manage.py makemigrations
python manage.py migrate

# 3. Criar usuário demo
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123') if not User.objects.filter(username='demo').exists() else print('Já existe')"

# 4. Popular dados
python populate_test_data.py

# 5. Iniciar servidor
python manage.py runserver
```

**Acesso:** http://localhost:8000  
**Usuário:** `demo`  
**Senha:** `demo123`

---

## 🔒 **GARANTIAS DE SEGURANÇA**

- ✅ Backup automático antes de qualquer alteração
- ✅ Dados de demo são **ADICIONADOS**, não substituídos
- ✅ Nenhum dado existente é modificado ou deletado
- ✅ Totalmente reversível usando o backup

📖 **Leia mais:** `GUIA_SEGURANCA_DEMO.md`

---

**🎉 Pronto! Sua versão de demonstração está configurada e segura!**

