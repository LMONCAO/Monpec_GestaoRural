# 🔄 Sincronização do Deploy com Localhost

## ✅ Status da Sincronização

O sistema está configurado para **automaticamente** manter o deploy sincronizado com o localhost:

### 1. **Settings Automáticos** ✅
- `settings_gcp.py` importa tudo de `settings.py` com `from .settings import *`
- Qualquer alteração em `settings.py` é automaticamente refletida em produção
- Configurações específicas do GCP são sobrescritas após a importação

### 2. **Dockerfile.prod Atualizado** ✅
- O Dockerfile.prod agora aceita `requirements_producao.txt` OU `requirements.txt`
- Se nenhum existir, instala dependências básicas automaticamente
- Coleta arquivos estáticos durante o build usando `settings.py` (base)

### 3. **Script de Deploy Atualizado** ✅
- `DEPLOY_GCP_COMPLETO.sh` usa o `Dockerfile.prod` existente
- Não cria Dockerfile novo, mantém o existente
- Configura variáveis de ambiente corretas para produção

## 📋 Como Manter Sincronizado

### Quando Fazer Atualização

Você precisa atualizar o deploy quando:
- ✅ Instalar novos pacotes Python (`pip install novo-pacote`)
- ✅ Adicionar novas migrações ao banco de dados
- ✅ Adicionar novos arquivos estáticos (CSS, JS, imagens)
- ✅ Alterar configurações em `settings.py` (já está automático)

### Processo de Atualização

#### 1. Gerar requirements.txt atualizado (se instalou novos pacotes)

```bash
# No ambiente localhost onde está funcionando
pip freeze > requirements.txt
```

#### 2. Verificar sincronização

```bash
chmod +x VERIFICAR_DEPLOY_ATUALIZADO.sh
./VERIFICAR_DEPLOY_ATUALIZADO.sh
```

#### 3. Fazer deploy

```bash
chmod +x DEPLOY_GCP_COMPLETO.sh
./DEPLOY_GCP_COMPLETO.sh
```

## 🔍 O que está sincronizado automaticamente

### ✅ Automático (não precisa fazer nada)

1. **Configurações do Django**
   - `settings_gcp.py` importa tudo de `settings.py`
   - INSTALLED_APPS, MIDDLEWARE, etc. são herdados

2. **Código da aplicação**
   - Todo código Python é copiado no build
   - Templates, arquivos estáticos originais, etc.

3. **Estrutura do projeto**
   - Mesma estrutura, mesmos apps

### ⚠️ Manual (precisa atualizar)

1. **Dependências Python** (se instalou novos pacotes)
   ```bash
   pip freeze > requirements.txt
   ```

2. **Migrações do banco** (após criar novas migrações)
   ```bash
   # O deploy aplica automaticamente, mas você pode verificar:
   python manage.py makemigrations
   python manage.py migrate
   ```

## 📝 Estrutura de Arquivos

```
projeto/
├── manage.py
├── requirements.txt              # ← Gerar quando instalar pacotes
├── requirements_producao.txt     # ← Opcional (pode usar requirements.txt)
├── Dockerfile.prod               # ← Já configurado e atualizado
├── sistema_rural/
│   ├── settings.py              # ← Configurações locais (base)
│   └── settings_gcp.py          # ← Importa settings.py + configurações GCP
├── DEPLOY_GCP_COMPLETO.sh       # ← Script de deploy atualizado
└── VERIFICAR_DEPLOY_ATUALIZADO.sh # ← Script para verificar sincronização
```

## 🚀 Fluxo Recomendado

### Desenvolvimento Local

1. Desenvolver e testar no localhost
2. Quando estiver funcionando corretamente:
   ```bash
   # 1. Gerar requirements (se necessário)
   pip freeze > requirements.txt
   
   # 2. Verificar sincronização
   ./VERIFICAR_DEPLOY_ATUALIZADO.sh
   
   # 3. Fazer commit (se usar git)
   git add .
   git commit -m "Atualização: [descrição das mudanças]"
   
   # 4. Deploy no GCP
   ./DEPLOY_GCP_COMPLETO.sh
   ```

## ✅ Checklist de Sincronização

Antes de fazer deploy, verifique:

- [ ] Sistema funcionando corretamente no localhost
- [ ] `requirements.txt` atualizado (se instalou novos pacotes)
- [ ] Migrações aplicadas localmente
- [ ] Testes passando (se houver)
- [ ] Arquivos estáticos coletados (`python manage.py collectstatic`)
- [ ] Sem erros ao executar `python manage.py check`

## 🔧 Scripts Disponíveis

1. **DEPLOY_GCP_COMPLETO.sh** - Deploy completo no Google Cloud
2. **VERIFICAR_DEPLOY_ATUALIZADO.sh** - Verifica se está sincronizado
3. **gerar_requirements.sh** - Gera requirements.txt do ambiente atual

## 💡 Dicas

- O `Dockerfile.prod` já está configurado para funcionar automaticamente
- `settings_gcp.py` herda tudo de `settings.py`, então configurações são sincronizadas
- Use `VERIFICAR_DEPLOY_ATUALIZADO.sh` antes de cada deploy para garantir
- Se instalar um pacote novo, gere `requirements.txt` novamente





