# 🔄 Como Atualizar o Script no Cloud Shell

## ⚠️ Problema

O script `DEPLOY_GCP_COMPLETO.sh` no Cloud Shell ainda está com a versão antiga que tenta usar `--file` (que não funciona).

## ✅ Solução

Você precisa fazer upload do script **corrigido** para o Cloud Shell.

### Opção 1: Upload Manual (Mais Rápido)

1. **No Cloud Shell, delete o script antigo:**
   ```bash
   rm DEPLOY_GCP_COMPLETO.sh
   ```

2. **Faça upload do script corrigido:**
   - Clique no ícone de menu (3 linhas) no canto superior direito do Cloud Shell
   - Selecione "Upload file"
   - Escolha o arquivo `DEPLOY_GCP_COMPLETO.sh` do seu computador
   - Aguarde o upload

3. **Dê permissão de execução:**
   ```bash
   chmod +x DEPLOY_GCP_COMPLETO.sh
   ```

4. **Execute novamente:**
   ```bash
   ./DEPLOY_GCP_COMPLETO.sh
   ```

### Opção 2: Copiar e Colar o Conteúdo

1. **Abra o arquivo corrigido no seu editor local**

2. **Copie TODO o conteúdo**

3. **No Cloud Shell, crie o arquivo:**
   ```bash
   nano DEPLOY_GCP_COMPLETO.sh
   ```

4. **Cole o conteúdo completo** (Ctrl+Shift+V no Cloud Shell)

5. **Salve e saia:**
   - Ctrl+O (salvar)
   - Enter (confirmar)
   - Ctrl+X (sair)

6. **Dê permissão:**
   ```bash
   chmod +x DEPLOY_GCP_COMPLETO.sh
   ```

7. **Execute:**
   ```bash
   ./DEPLOY_GCP_COMPLETO.sh
   ```

### Opção 3: Usar Git (Se o projeto estiver no Git)

Se o projeto estiver em um repositório Git:

```bash
# Fazer pull das atualizações
git pull origin main

# Ou se já tiver o repositório clonado
cd Monpec_GestaoRural
git pull
```

## 🔍 Verificar se Está Corrigido

Antes de executar, verifique se o script não tem mais `--file`:

```bash
grep -n "--file" DEPLOY_GCP_COMPLETO.sh
```

Se não retornar nada, está correto! ✅

Se retornar linhas, o script ainda está com erro.

## ✅ O que foi corrigido

A correção remove completamente o uso de `--file` e em vez disso:
1. Copia `Dockerfile.prod` para `Dockerfile` temporariamente
2. Executa `gcloud builds submit --tag IMAGE_TAG` (sem --file)
3. Restaura o Dockerfile original após o build

## 🚀 Após atualizar

Execute o script e o build deve funcionar corretamente!

```bash
./DEPLOY_GCP_COMPLETO.sh
```





