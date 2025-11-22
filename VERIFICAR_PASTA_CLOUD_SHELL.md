# 🔍 Verificar Pasta no Cloud Shell

## ⚠️ Erro: Pasta não encontrada

O erro `-bash: cd: Monpec_GestaoRural: No such file or directory` significa que a pasta não existe no Cloud Shell.

---

## 🔍 Passo 1: Verificar o que existe no Cloud Shell

Execute este comando no Cloud Shell:

```bash
ls -la
```

Isso vai mostrar todos os arquivos e pastas na pasta atual.

---

## 📁 Passo 2: Identificar a pasta do projeto

Procure por:
- Pasta com o código do projeto
- Arquivos como `manage.py`, `Dockerfile`, `requirements_producao.txt`

Possíveis nomes de pasta:
- `Monpec_GestaoRural`
- `monpec-gestao-rural`
- Nome que você deu ao fazer upload
- Ou os arquivos podem estar na pasta atual (`~`)

---

## ✅ Passo 3: Corrigir o comando baseado no que encontrar

### **Se os arquivos estão na pasta atual:**

```bash
# Corrigir requirements_producao.txt
sed -i 's/^django-logging==0.1.0/# django-logging==0.1.0  # Removido: pacote não existe/' requirements_producao.txt

# Corrigir Dockerfile
sed -i '/pip install --no-cache-dir gunicorn$/d' Dockerfile

echo "✅ Arquivos corrigidos!"
```

### **Se a pasta tem outro nome (exemplo: "meu-projeto"):**

```bash
cd nome-da-pasta-encontrada
sed -i 's/^django-logging==0.1.0/# django-logging==0.1.0  # Removido: pacote não existe/' requirements_producao.txt
sed -i '/pip install --no-cache-dir gunicorn$/d' Dockerfile
echo "✅ Arquivos corrigidos!"
```

---

## 📤 Se não encontrar nada: Fazer Upload

Se não encontrar os arquivos, você precisa fazer upload:

1. No Cloud Shell, clique nos **3 pontos (⋮)** no canto superior direito
2. Selecione **"Upload file"** ou **"Upload folder"**
3. Faça upload da pasta `Monpec_GestaoRural` do seu computador
4. Depois execute o comando de correção novamente

---

## 🚀 Comando Completo (ajuste o nome da pasta)

Depois de encontrar a pasta, execute:

```bash
# Substituir "NOME_DA_PASTA" pelo nome real encontrado
cd NOME_DA_PASTA && \
sed -i 's/^django-logging==0.1.0/# django-logging==0.1.0  # Removido: pacote não existe/' requirements_producao.txt && \
sed -i '/^django-logging==0.1.0$/d' requirements_producao.txt && \
sed -i '/pip install --no-cache-dir gunicorn$/d' Dockerfile && \
echo "✅ Arquivos corrigidos! Agora execute: gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec"
```

---

**Primeiro, execute `ls -la` para ver o que existe no Cloud Shell!**

