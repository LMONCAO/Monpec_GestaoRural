# 📋 Instruções para Executar Deploy no Google Cloud Shell

## ⚠️ Problema Comum

Se você recebeu o erro: `❌ ERRO: manage.py não encontrado!`

Isso significa que o script foi executado no diretório home (`~`) ao invés do diretório do projeto Django.

## ✅ Solução

### Opção 1: Se o código JÁ está no Cloud Shell

1. **Navegue até o diretório do projeto:**
   ```bash
   # Liste os diretórios disponíveis
   ls -la
   
   # Navegue até o diretório do projeto (ajuste o nome se necessário)
   cd Monpec_GestaoRural
   # ou
   cd monpec-gestao-rural
   # ou qualquer outro nome que você tenha
   ```

2. **Verifique se está no lugar certo:**
   ```bash
   ls manage.py
   # Se aparecer "manage.py", você está no lugar certo!
   ```

3. **Execute o script novamente:**
   ```bash
   bash ~/DEPLOY_CORRECOES_DEMO.sh
   ```

### Opção 2: Fazer Clone do Repositório Git

Se o código ainda não está no Cloud Shell, faça clone:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   ```

2. **Entre no diretório:**
   ```bash
   cd SEU_REPOSITORIO
   ```

3. **Faça upload do script para dentro do projeto:**
   - Use o menu Upload do Cloud Shell
   - Ou copie o script diretamente:
     ```bash
     # Se o script está na home, copie para o diretório do projeto
     cp ~/DEPLOY_CORRECOES_DEMO.sh .
     ```

4. **Execute o script:**
   ```bash
   bash DEPLOY_CORRECOES_DEMO.sh
   ```

### Opção 3: Copiar o Código para o Cloud Shell

Se você tem o código localmente:

1. **Faça upload de todos os arquivos do projeto:**
   - Use o menu do Cloud Shell (☰) → Upload
   - Selecione todos os arquivos do projeto
   - Ou use um arquivo ZIP e extraia no Cloud Shell

2. **Navegue até o diretório:**
   ```bash
   cd Monpec_GestaoRural  # ou nome do diretório
   ```

3. **Execute o script:**
   ```bash
   bash DEPLOY_CORRECOES_DEMO.sh
   ```

## 🔍 Verificar se Está no Diretório Correto

Execute estes comandos para verificar:

```bash
# Ver diretório atual
pwd

# Listar arquivos
ls -la

# Verificar se manage.py existe
ls manage.py

# Verificar se Dockerfile.prod existe
ls Dockerfile.prod
```

Se todos os arquivos existirem, você está no lugar certo! ✅

## 📝 Comandos Rápidos

**Sequência completa (se o código já está no Cloud Shell):**

```bash
# 1. Ver onde você está
pwd

# 2. Listar diretórios
ls -la

# 3. Navegar até o projeto (ajuste o nome)
cd Monpec_GestaoRural

# 4. Verificar arquivos
ls manage.py Dockerfile.prod

# 5. Executar o script (se estiver na home)
bash ~/DEPLOY_CORRECOES_DEMO.sh

# OU se copiou o script para dentro do projeto:
bash DEPLOY_CORRECOES_DEMO.sh
```

## 🚨 Erros Comuns

### Erro: "manage.py não encontrado"
- **Causa:** Script executado no diretório errado
- **Solução:** Navegue até o diretório do projeto Django

### Erro: "Dockerfile.prod não encontrado"
- **Causa:** Arquivos do projeto incompletos
- **Solução:** Certifique-se de fazer upload/copy de todos os arquivos

### Erro: "Permission denied"
- **Causa:** Script não tem permissão de execução
- **Solução:** `chmod +x DEPLOY_CORRECOES_DEMO.sh`

## ✅ Checklist Antes de Executar

Antes de executar o script, certifique-se de:

- [ ] Você está no diretório raiz do projeto Django
- [ ] O arquivo `manage.py` existe
- [ ] O arquivo `Dockerfile.prod` existe
- [ ] O arquivo `DEPLOY_CORRECOES_DEMO.sh` está disponível
- [ ] Você está autenticado no Google Cloud (`gcloud auth list`)

## 🎯 Próximos Passos

Depois que o script executar com sucesso:

1. Aguarde o build completar (15-25 minutos)
2. Aguarde o deploy completar (3-10 minutos)
3. Aguarde 1-2 minutos para o serviço inicializar
4. Teste o login com usuário demo
5. Verifique que o sistema reconhece corretamente como usuário demo

---

**Dica:** Se você sempre trabalha com o mesmo projeto, pode criar um alias no Cloud Shell:

```bash
# Adicionar ao ~/.bashrc
echo "alias cdmonpec='cd ~/Monpec_GestaoRural'" >> ~/.bashrc
source ~/.bashrc

# Depois basta usar:
cdmonpec
```


