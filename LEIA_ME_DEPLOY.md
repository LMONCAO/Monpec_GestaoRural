# 🚀 Deploy Completo Automático - Google Cloud

## ⚡ Início Rápido

### 🌐 Para fazer deploy direto no Google Cloud Shell:
**Abra o arquivo:** `COLE_AQUI_GOOGLE_CLOUD_SHELL.txt` ou `COMANDOS_PARA_GOOGLE_CLOUD_SHELL.md`
- Copie o código e cole no Google Cloud Shell
- Mais rápido e direto
- Não precisa do computador local

### ⚠️ Se o deploy não atualizou o sistema (mudanças não aparecem):
```cmd
FORCAR_ATUALIZACAO_COMPLETA.bat
```
**Este script força uma atualização completa garantindo que a versão nova seja aplicada.**

### Para fazer deploy normal (do computador local):
```cmd
DEPLOY_GARANTIR_VERSAO_CORRETA.bat
```

### Para acompanhar o deploy:
```cmd
ACOMPANHAR_DEPLOY_COMPLETO.bat
```

### Para validar se a atualização foi aplicada:
```cmd
VALIDAR_ATUALIZACAO.bat
```

---

## 📋 Scripts Disponíveis

### ⭐ `DEPLOY_GARANTIR_VERSAO_CORRETA.bat` ou `.ps1` (RECOMENDADO - Garante versão correta)
- ✅ Verifica se está na pasta correta
- ✅ Valida Dockerfile
- ✅ Limpa cache de build (--no-cache)
- ✅ Faz build garantindo versão nova
- ✅ Faz deploy completo
- ✅ **GARANTE que a versão do localhost será deployada**

**Como usar:**
- **Windows CMD:** Execute: `DEPLOY_GARANTIR_VERSAO_CORRETA.bat`
- **PowerShell:** Execute: `.\DEPLOY_GARANTIR_VERSAO_CORRETA.ps1`
- Aguarde (pode levar 15-25 minutos com --no-cache)
- Pronto! Sistema funcionando com a versão correta

---

### 1. `DEPLOY_COMPLETO_AUTOMATICO.bat` (Recomendado para iniciantes)
- ✅ Limpa arquivos antigos no Cloud
- ✅ Faz upload completo da pasta
- ✅ Cria script para Cloud Shell
- ⚠️ Requer executar comandos no Cloud Shell depois

**Como usar:**
1. Execute: `DEPLOY_COMPLETO_AUTOMATICO.bat`
2. Aguarde o upload terminar
3. Abra o Google Cloud Shell
4. Execute o script criado ou os comandos mostrados

---

### 2. `DEPLOY_TUDO_AUTOMATICO.bat` (Tudo automático - RECOMENDADO) ⭐
- ✅ Limpa arquivos antigos
- ✅ Faz upload para backup
- ✅ Faz build da imagem Docker com **TODOS os arquivos do localhost**
- ✅ Faz deploy no Cloud Run com configurações corretas
- ✅ Inclui SECRET_KEY e todas as variáveis de ambiente necessárias
- ✅ Tudo automático, sem precisar do Cloud Shell!
- ✅ **Atualiza produção com a versão exata do localhost**

**Como usar:**
1. Execute: `DEPLOY_TUDO_AUTOMATICO.bat`
2. Aguarde (pode levar 10-20 minutos)
3. Pronto! Sistema funcionando na web com a versão do localhost

---

## ⚙️ Configurações

Os scripts usam estas configurações (já definidas):

- **Projeto:** `monpec-sistema-rural`
- **Serviço:** `monpec`
- **Região:** `us-central1`
- **Banco de Dados:** `monpec-db`

Se precisar alterar, edite as variáveis no início dos scripts `.bat`.

---

## 📦 Pré-requisitos

1. **Google Cloud SDK instalado**
   - Baixe: https://cloud.google.com/sdk/docs/install
   - Ou: `winget install Google.CloudSDK`

2. **Autenticado no Google Cloud**
   - ⚠️ **IMPORTANTE:** Se o Google Cloud fica pedindo senha toda hora, execute primeiro:
     - `CONFIGURAR_AUTENTICACAO_PERSISTENTE.bat` (configura uma vez, não pede mais senha)
   - Ou manualmente:
     - Execute: `gcloud auth login`
     - Execute: `gcloud auth application-default login` (evita pedir senha toda hora)
   - Configure projeto: `gcloud config set project monpec-sistema-rural`
   - 📖 Veja: `SOLUCAO_AUTENTICACAO_GOOGLE_CLOUD.md` para mais detalhes

3. **APIs habilitadas** (o script faz isso automaticamente)
   - Cloud Build API
   - Cloud Run API
   - Cloud SQL Admin API

---

## 🔄 O que os scripts fazem

### `DEPLOY_COMPLETO_AUTOMATICO.bat`:
1. Verifica ferramentas (gcloud, gsutil)
2. Autentica e configura projeto
3. **Limpa bucket antigo** (remove tudo que estava lá)
4. Cria bucket se não existir
5. **Faz upload completo** da pasta local
6. Cria script para Cloud Shell
7. Mostra instruções

### `DEPLOY_TUDO_AUTOMATICO.bat`:
1. Verifica ferramentas (gcloud)
2. Autentica e configura projeto
3. Habilita APIs necessárias
4. **Limpa bucket antigo**
5. Faz backup no Cloud Storage (inclui TODOS os arquivos do localhost)
6. **Build da imagem Docker** (usa arquivos do diretório atual)
7. **Deploy no Cloud Run** (com SECRET_KEY e todas as variáveis de ambiente)
8. Verifica status e mostra URL

---

## 🎯 Qual usar?

- **Use `FORCAR_ATUALIZACAO_COMPLETA.bat`** ⚠️ **SE O DEPLOY NÃO ATUALIZOU O SISTEMA** (mudanças não aparecem) - **FORÇA atualização completa**
- **Use `DEPLOY_GARANTIR_VERSAO_CORRETA.bat`** ⭐ se acabou de restaurar o sistema ou quer garantir que a versão correta seja deployada (RECOMENDADO)
- **Use `DEPLOY_TUDO_AUTOMATICO.bat`** se quer tudo automático e não quer usar Cloud Shell
- **Use `DEPLOY_COMPLETO_AUTOMATICO.bat`** se prefere fazer o deploy manualmente no Cloud Shell

---

## ⚠️ Importante

- Os scripts **excluem automaticamente** arquivos desnecessários:
  - `venv/`, `__pycache__/`, `.git/`, `node_modules/`
  - `*.pyc`, `.env`, `logs/`, `temp/`, `staticfiles/`

- O deploy pode levar **10-20 minutos** dependendo do tamanho do projeto

- Certifique-se de que o **banco de dados Cloud SQL** já existe e está configurado

---

## ⚠️ PROBLEMA: Deploy não atualizou o sistema?

**Se você fez deploy mas as mudanças não aparecem no servidor, use este script:**

```cmd
FORCAR_ATUALIZACAO_COMPLETA.bat
```

**O que este script faz:**
- ✅ Cria uma tag única (timestamp) para garantir nova imagem
- ✅ Faz build SEM CACHE (--no-cache)
- ✅ Cria nova revisão no Cloud Run com --no-traffic
- ✅ Redireciona 100% do tráfego para a nova revisão
- ✅ Valida se a atualização foi aplicada

**Depois de executar:**
1. Aguarde 2-3 minutos para o serviço inicializar
2. **Limpe o cache do navegador** (Ctrl+F5 ou Ctrl+Shift+R)
3. Acesse a URL do servidor
4. Verifique se as mudanças aparecem

**Para validar se funcionou:**
```cmd
VALIDAR_ATUALIZACAO.bat
```

---

## 🔄 Garantir que a Versão Correta seja Deployada

**IMPORTANTE:** Se você acabou de restaurar o sistema ou extraiu novos arquivos, siga estes passos para garantir que a versão correta suba para o Google Cloud:

### 1. Certifique-se de estar na pasta correta

Se você rodar o deploy na pasta errada (ex: pasta pai `L_MONCAOSILVA`), ele pode tentar subir arquivos residuais antigos. **Sempre entre na pasta onde você extraiu o ZIP:**

```bash
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

**No PowerShell:**
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

### 2. Limpe o Cache de Build

Às vezes, o Google Cloud reutiliza "camadas" de uma versão anterior. Use o comando abaixo para forçar a criação de uma versão totalmente nova:

```bash
gcloud builds submit --no-cache --tag gcr.io/$(gcloud config get-value project)/sistema-rural .
```

**No PowerShell:**
```powershell
$PROJECT = gcloud config get-value project
gcloud builds submit --no-cache --tag "gcr.io/$PROJECT/sistema-rural" .
```

### 3. Verifique o arquivo Dockerfile

- **Apague qualquer Dockerfile antigo** que possa estar na pasta principal (pasta pai)
- **Garanta que o `Dockerfile.prod` dentro de `Monpec_GestaoRural` é o correto**
- Se você tem um arquivo chamado `Dockerfile_(2).prod` ou similar, renomeie para `Dockerfile.prod` ou apague o antigo

**Verificar qual Dockerfile está sendo usado:**
```bash
# No diretório Monpec_GestaoRural
ls -la Dockerfile*
```

### 4. Execute o Deploy apontando para a pasta atual

Após subir a imagem no passo 2, execute o deploy:

```bash
gcloud run deploy monpec-sistema-rural --image gcr.io/$(gcloud config get-value project)/sistema-rural --platform managed
```

**No PowerShell:**
```powershell
$PROJECT = gcloud config get-value project
gcloud run deploy monpec-sistema-rural --image "gcr.io/$PROJECT/sistema-rural" --platform managed
```

### 5. Como confirmar que é a versão nova?

Para ter certeza, você pode alterar uma palavra simples no código antes de rodar o deploy:

1. Abra um arquivo de template (ex: `templates/site/landing_page.html`)
2. Mude um texto visível (ex: um título na tela inicial)
3. Salve o arquivo
4. Rode o deploy novamente
5. Acesse a URL e verifique se a mudança aparece

**Ou use o script automático que já faz isso:**
```cmd
DEPLOY_TUDO_AUTOMATICO.bat
```

Este script já garante que está usando os arquivos do diretório atual e limpa o cache automaticamente.

---

## 🐛 Troubleshooting

### Erro: "gcloud não encontrado"
- Instale o Google Cloud SDK
- Reinicie o terminal após instalar

### Erro: "Não autenticado"
- Execute: `gcloud auth login`
- Escolha sua conta Google

### Erro: "Bucket não encontrado"
- O script cria automaticamente, mas verifique permissões

### Erro no build
- Verifique se o `Dockerfile.prod` existe
- Verifique se `requirements_producao.txt` está correto

### Erro no deploy
- Verifique se o Cloud SQL está configurado
- Verifique as variáveis de ambiente no script

---

## 📊 Acompanhar o Deploy

### 🎯 Script Principal: `ACOMPANHAR_DEPLOY_COMPLETO.bat` ⭐ (RECOMENDADO)

**O script mais completo para acompanhar tudo:**
- ✅ Mostra resumo rápido do status
- ✅ Menu interativo com opções
- ✅ **NÃO fecha automaticamente** - você pode ver todas as informações
- ✅ Permite voltar ao menu após cada ação

**Como usar:**
```cmd
ACOMPANHAR_DEPLOY_COMPLETO.bat
```

Este script oferece um menu interativo com:
1. Acompanhar BUILD em tempo real (fica aberto mostrando progresso)
2. Acompanhar LOGS do servico em tempo real (fica aberto mostrando logs)
3. Ver status completo do servico
4. Ver erros especificos
5. **Monitorar servidor** (atualiza automaticamente a cada 10 segundos)
6. Sair

---

### 🔴 `MONITORAR_SERVIDOR_TEMPO_REAL.bat` ⭐⭐ (MELHOR PARA VER EM TEMPO REAL)

**Script que fica aberto atualizando automaticamente:**
- ✅ **Fica aberto** mostrando informações atualizadas
- ✅ Atualiza automaticamente a cada 10 segundos
- ✅ Mostra: Status do serviço, Builds recentes, Revisões, Logs recentes
- ✅ **NÃO fecha** - você vê tudo em tempo real
- ✅ Pressione Ctrl+C para sair

**Como usar:**
```cmd
MONITORAR_SERVIDOR_TEMPO_REAL.bat
```

**Ideal para:** Acompanhar o servidor enquanto está rodando, ver mudanças em tempo real.

---

### 📺 `VER_LOGS_TEMPO_REAL.bat` - Logs em Tempo Real

**Script dedicado apenas para logs:**
- ✅ Fica aberto mostrando logs conforme aparecem
- ✅ **NÃO fecha automaticamente**
- ✅ Mostra logs do servidor em tempo real
- ✅ Pressione Ctrl+C para parar

**Como usar:**
```cmd
VER_LOGS_TEMPO_REAL.bat
```

---

### 🔨 `ACOMPANHAR_BUILD_TEMPO_REAL.bat` - Build em Tempo Real

**Script dedicado para acompanhar builds:**
- ✅ Mostra builds recentes
- ✅ Permite escolher qual build acompanhar
- ✅ Fica aberto mostrando progresso do build
- ✅ **NÃO fecha automaticamente**
- ✅ Pressione Ctrl+C para parar

**Como usar:**
```cmd
ACOMPANHAR_BUILD_TEMPO_REAL.bat
```

---

### 📦 Durante o Build (Enquanto está construindo a imagem)

**1. `ACOMPANHAR_BUILD.bat`** - Acompanhar build em tempo real
- ✅ Mostra builds recentes
- ✅ Permite acompanhar um build específico em tempo real
- ✅ Útil enquanto o `gcloud builds submit` está rodando

**Como usar:**
```cmd
ACOMPANHAR_BUILD.bat
```

**Ou use diretamente no terminal:**
```cmd
# Ver builds recentes
gcloud builds list --limit=5

# Acompanhar build mais recente em tempo real
gcloud builds log --stream

# Acompanhar um build específico
gcloud builds log [BUILD_ID] --stream
```

---

### 🚀 Após o Deploy (Quando o serviço já está rodando)

**1. `VERIFICAR_DEPLOY.bat`** - Status completo do serviço
- ✅ Verifica status do serviço
- ✅ Mostra URL do sistema
- ✅ Lista revisões (versões) recentes
- ✅ Mostra logs recentes
- ✅ Testa se o serviço está respondendo

**Como usar:**
```cmd
VERIFICAR_DEPLOY.bat
```

**2. `VER_LOGS_DEPLOY.bat`** - Logs em tempo real
- ✅ Mostra logs em tempo real do servico
- ✅ Útil para acompanhar o que está acontecendo
- ✅ Atualiza automaticamente

**Como usar:**
```cmd
VER_LOGS_DEPLOY.bat
```
(Pressione Ctrl+C para parar)

**3. `VERIFICAR_ERROS_DEPLOY.bat`** - Buscar erros específicos
- ✅ Busca erros específicos nos logs
- ✅ Verifica condições do serviço
- ✅ Mostra status do último build
- ✅ Filtra apenas erros, exceções e problemas

**Como usar:**
```cmd
VERIFICAR_ERROS_DEPLOY.bat
```

---

### 📋 Resumo dos Scripts de Acompanhamento

| Script | Quando Usar | O que Faz | Fica Aberto? |
|--------|-------------|-----------|--------------|
| `ACOMPANHAR_DEPLOY_GOOGLE_CLOUD.bat` | **Ver no navegador** 🌐 | Abre links do Google Cloud Console | ⚠️ Abre navegador |
| `VER_ERROS_FINAIS.bat` | **Ver erros** 🔴 | Mostra apenas erros do deploy | ⚠️ Pausa |
| `MONITORAR_ERROS_FINAL.bat` | **Acompanhar e ver erros** | Monitora e mostra erros no final | ✅ SIM |
| `MONITORAR_SERVIDOR_TEMPO_REAL.bat` | **Sempre** ⭐⭐ | Atualiza automaticamente a cada 10s | ✅ SIM |
| `ACOMPANHAR_DEPLOY_COMPLETO.bat` | **Sempre** ⭐ | Menu interativo completo | ✅ SIM (menu) |
| `VER_LOGS_TEMPO_REAL.bat` | Ver logs | Logs em tempo real | ✅ SIM |
| `ACOMPANHAR_BUILD_TEMPO_REAL.bat` | Durante build | Acompanha build em tempo real | ✅ SIM |
| `VERIFICAR_DEPLOY.bat` | Após deploy | Status completo do serviço | ⚠️ Pausa |
| `VER_LOGS_DEPLOY.bat` | Durante/Depois | Logs em tempo real | ✅ SIM |
| `VERIFICAR_ERROS_DEPLOY.bat` | Se houver problemas | Busca erros específicos | ⚠️ Pausa |

---

### 🌐 Acompanhar no Google Cloud Console

**`ACOMPANHAR_DEPLOY_GOOGLE_CLOUD.bat`** - Abre links do Google Cloud Console
- ✅ Abre Cloud Build (ver builds e erros)
- ✅ Abre Cloud Run (ver serviço e revisões)
- ✅ Abre Logs (ver logs em tempo real)
- ✅ Abre Erros (filtrar apenas erros)
- ✅ Abre Container Registry (ver imagens)

**Como usar:**
```cmd
ACOMPANHAR_DEPLOY_GOOGLE_CLOUD.bat
```

Este script abre todos os links importantes do Google Cloud Console onde você pode acompanhar o deploy visualmente.

---

### 🔴 Ver Erros no Final

**`VER_ERROS_FINAIS.bat`** - Mostra apenas erros do deploy
- ✅ Mostra erros do build
- ✅ Mostra erros do serviço
- ✅ Mostra revisões com problemas
- ✅ Abre links do Google Cloud Console para ver mais detalhes

**Como usar:**
```cmd
VER_ERROS_FINAIS.bat
```

**`MONITORAR_ERROS_FINAL.bat`** - Monitora deploy e mostra erros no final
- ✅ Acompanha o build em tempo real
- ✅ Monitora o deploy
- ✅ Mostra resumo de erros no final
- ✅ Mostra status completo

**Como usar:**
```cmd
MONITORAR_ERROS_FINAL.bat
```

---

### 🔍 Comandos Manuais Úteis

**Ver status do build:**
```cmd
gcloud builds list --limit=5
```

**Acompanhar build em tempo real:**
```cmd
gcloud builds log --stream
```

**Ver status do serviço:**
```cmd
gcloud run services describe monpec --region=us-central1
```

**Ver URL do serviço:**
```cmd
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

**Ver logs recentes:**
```cmd
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50
```

**Ver logs em tempo real:**
```cmd
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"
```

**Ver revisões (versões):**
```cmd
gcloud run revisions list --service=monpec --region=us-central1 --limit=5
```

**Ver apenas erros:**
```cmd
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50
```

---

## 📞 Suporte e Troubleshooting

### Se tiver problemas durante o deploy:

1. **Durante o BUILD:**
   ```cmd
   ACOMPANHAR_BUILD.bat
   ```
   Ou: `gcloud builds log --stream`

2. **Após o deploy:**
   ```cmd
   ACOMPANHAR_DEPLOY_COMPLETO.bat
   ```
   Este script mostra tudo e oferece opções para investigar

3. **Se o serviço não está funcionando:**
   ```cmd
   VERIFICAR_ERROS_DEPLOY.bat
   ```
   Busca erros específicos nos logs

4. **Para ver logs em tempo real:**
   ```cmd
   VER_LOGS_DEPLOY.bat
   ```

### Comandos úteis para diagnóstico:

- **Status geral:** `VERIFICAR_DEPLOY.bat`
- **Erros específicos:** `VERIFICAR_ERROS_DEPLOY.bat`
- **Logs em tempo real:** `VER_LOGS_DEPLOY.bat`
- **Builds:** `gcloud builds list --limit=5`
- **Status do serviço:** `gcloud run services describe monpec --region=us-central1`

---

## ✅ Após o Deploy

O sistema estará disponível em uma URL como:
```
https://monpec-XXXXX-uc.a.run.app
```

**Credenciais de Admin:**
- Usuário: `admin`
- Senha: `L6171r12@@`

**Para verificar se está funcionando:**
1. Execute: `VERIFICAR_DEPLOY.bat` (mostra status e URL)
2. Aguarde 1-2 minutos para o serviço inicializar
3. Acesse a URL no navegador
4. Teste o login com as credenciais acima

**Você pode ver a URL executando:**
```cmd
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

**Importante:**
- O sistema executa migrações automaticamente no início
- Aguarde 1-2 minutos após o deploy para o serviço inicializar completamente
- Todos os arquivos do localhost (templates, static, etc.) são incluídos no deploy
- Se algo não funcionar, execute `VERIFICAR_ERROS_DEPLOY.bat` para diagnosticar

