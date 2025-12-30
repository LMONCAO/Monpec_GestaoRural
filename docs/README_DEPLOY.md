# 🚀 Guia de Deploy - Sistema MONPEC

Este guia explica como fazer o deploy e corrigir problemas do sistema MONPEC.

## 📋 Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL (para produção) ou SQLite (para desenvolvimento)
- Dependências instaladas (`requirements.txt`)

## 🔧 Scripts Disponíveis

### 1. Deploy e Correção Completa

Execute este script para fazer o deploy completo e corrigir problemas:

**Windows (PowerShell):**
```powershell
.\DEPLOY_E_CORRIGIR.ps1
```

**Windows (Batch):**
```batch
DEPLOY_E_CORRIGIR.bat
```

Este script:
- ✅ Verifica e instala dependências
- ✅ Configura variáveis de ambiente
- ✅ Verifica conexão com banco de dados
- ✅ Aplica migrações
- ✅ Coleta arquivos estáticos
- ✅ Verifica configurações

### 2. Verificar e Corrigir Problemas

Execute para diagnosticar e corrigir problemas:

**Windows (PowerShell):**
```powershell
.\VERIFICAR_E_CORRIGIR.ps1
```

### 3. Iniciar Servidor em Produção

Após o deploy, inicie o servidor:

**Windows (PowerShell):**
```powershell
.\INICIAR_SERVIDOR_PRODUCAO.ps1
```

**Windows (Batch):**
```batch
INICIAR_SERVIDOR_PRODUCAO.bat
```

## ⚙️ Configuração de Variáveis de Ambiente

Crie um arquivo `.env_producao` na raiz do projeto com as seguintes variáveis:

```env
# Chave secreta Django (OBRIGATÓRIO em produção!)
SECRET_KEY=sua-chave-secreta-aqui

# Modo debug (False em produção)
DEBUG=False

# Configurações do banco de dados (PostgreSQL)
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=sua-senha-aqui
DB_HOST=localhost
DB_PORT=5432

# Configurações do Mercado Pago (opcional)
MERCADOPAGO_ACCESS_TOKEN=seu-token-aqui
MERCADOPAGO_PUBLIC_KEY=sua-chave-publica-aqui
```

## 🔍 Solução de Problemas

### Erro: "Internal Server Error"

1. **Verifique os logs:**
   ```powershell
   Get-Content logs\django.log -Tail 50
   ```

2. **Verifique as migrações:**
   ```powershell
   python manage.py showmigrations --settings=sistema_rural.settings_producao
   ```

3. **Aplique migrações manualmente:**
   ```powershell
   python manage.py migrate --settings=sistema_rural.settings_producao
   ```

4. **Colete arquivos estáticos:**
   ```powershell
   python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
   ```

### Erro: "SECRET_KEY não configurada"

Configure a variável de ambiente `SECRET_KEY` no arquivo `.env_producao` ou exporte:
```powershell
$env:SECRET_KEY="sua-chave-secreta-aqui"
```

### Erro: "Database connection failed"

1. Verifique se o PostgreSQL está rodando
2. Verifique as credenciais no `.env_producao`
3. Teste a conexão:
   ```powershell
   python manage.py dbshell --settings=sistema_rural.settings_producao
   ```

### Erro: "Static files not found"

Execute:
```powershell
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
```

## 📝 Passos Manuais de Deploy

Se preferir fazer manualmente:

1. **Instalar dependências:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente:**
   - Crie `.env_producao` ou exporte as variáveis

3. **Aplicar migrações:**
   ```powershell
   python manage.py migrate --settings=sistema_rural.settings_producao
   ```

4. **Coletar arquivos estáticos:**
   ```powershell
   python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
   ```

5. **Verificar configurações:**
   ```powershell
   python manage.py check --settings=sistema_rural.settings_producao --deploy
   ```

6. **Iniciar servidor:**
   ```powershell
   python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao
   ```

## 🌐 Deploy em Produção (Cloud Run / Servidor Linux)

Para deploy no Google Cloud Run ou servidor Linux, consulte:
- `DEPLOY_COMPLETO.sh` - Script para Cloud Run
- `Dockerfile.prod` - Dockerfile para produção

## ⚠️ Importante

- **NUNCA** use `DEBUG=True` em produção
- **SEMPRE** configure `SECRET_KEY` em produção
- **SEMPRE** use HTTPS em produção (configure SSL)
- **SEMPRE** faça backup do banco de dados antes de migrações

## 📞 Suporte

Em caso de problemas:
1. Execute `VERIFICAR_E_CORRIGIR.ps1` para diagnóstico
2. Verifique os logs em `logs/django.log`
3. Verifique as configurações em `sistema_rural/settings_producao.py`
