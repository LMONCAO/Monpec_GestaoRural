# 🚀 Guia Completo: Trabalhar com a Pasta Sincronizada no GitHub

## 📋 Visão Geral

Esta pasta (`Monpec_GestaoRural`) está conectada ao repositório GitHub:
- **Repositório**: https://github.com/LMONCAO/Monpec_GestaoRural.git
- **Branch Principal**: `main` ou `master`

## 🎯 Objetivo

Trabalhar nesta pasta e manter tudo sincronizado com o GitHub, garantindo que:
1. ✅ Todas as alterações sejam salvas no GitHub
2. ✅ Você sempre tenha a versão mais recente
3. ✅ O sistema funcione corretamente a partir desta pasta

---

## 📥 **PASSO 1: Garantir que está Sincronizado**

### Opção A: Usando GitHub Desktop (Recomendado)

1. **Abra o GitHub Desktop**
2. **Selecione este repositório** (`Monpec_GestaoRural`)
3. **Faça Pull para pegar atualizações:**
   - Clique em `Repository` → `Pull` (ou `Ctrl + Shift + P`)
   - Isso baixa todas as alterações do GitHub

### Opção B: Usando Git Bash ou Terminal

Se você tem Git instalado, abra o terminal nesta pasta e execute:

```bash
git pull origin main
```

---

## 🛠️ **PASSO 2: Configurar o Ambiente Python**

### 2.1. Verificar Python

Abra o PowerShell nesta pasta e verifique:

```powershell
python --version
```

Deve mostrar Python 3.8 ou superior.

### 2.2. Criar Ambiente Virtual (Recomendado)

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
```

### 2.3. Instalar Dependências

```powershell
pip install -r requirements.txt
```

---

## 🚀 **PASSO 3: Configurar o Banco de Dados**

### 3.1. Executar Migrações

```powershell
python manage.py migrate
```

### 3.2. Criar Superusuário (se necessário)

```powershell
python manage.py createsuperuser
```

Ou use o script pronto:

```powershell
python criar_superusuario.py
```

---

## ▶️ **PASSO 4: Iniciar o Sistema**

### Opção 1: Usando o Script Batch (Windows)

```powershell
.\INICIAR_SISTEMA.bat
```

### Opção 2: Comando Manual

```powershell
python manage.py runserver
```

O sistema estará disponível em: **http://127.0.0.1:8000/**

---

## 🔄 **PASSO 5: Fluxo de Trabalho Diário**

### 🌅 **Início do Dia**

1. **Abrir GitHub Desktop**
2. **Fazer Pull** para pegar atualizações:
   - `Repository` → `Pull` (ou `Ctrl + Shift + P`)
3. **Abrir o Cursor/VS Code** nesta pasta
4. **Ativar ambiente virtual** (se usar):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
5. **Iniciar o servidor**:
   ```powershell
   python manage.py runserver
   ```

### 💻 **Durante o Trabalho**

- Faça suas alterações normalmente
- O GitHub Desktop detecta automaticamente as mudanças
- Teste o sistema localmente antes de commitar

### 📤 **Ao Terminar uma Tarefa**

1. **Parar o servidor** (Ctrl + C no terminal)
2. **Abrir GitHub Desktop**
3. **Revisar alterações** na aba "Changes"
4. **Adicionar mensagem de commit** descritiva:
   ```
   Exemplo: "Adiciona funcionalidade de relatórios personalizados"
   ```
5. **Fazer Commit**:
   - Clique em "Commit to main"
6. **Fazer Push** para enviar ao GitHub:
   - Clique em "Push origin" (ou `Ctrl + P`)

### 🌙 **Fim do Dia**

1. **Certifique-se de que todos os commits foram enviados**
2. **Verifique se não há alterações pendentes**
3. **Faça um último Push se necessário**

---

## 📝 **Comandos Úteis do Git**

### Ver Status

```bash
git status
```

### Adicionar Arquivos

```bash
git add .
```

### Fazer Commit

```bash
git commit -m "Sua mensagem aqui"
```

### Enviar para GitHub

```bash
git push origin main
```

### Baixar do GitHub

```bash
git pull origin main
```

---

## ⚠️ **Solução de Problemas**

### Problema: "Git não é reconhecido"

**Solução**: Instale o Git ou use GitHub Desktop

1. Baixe Git: https://git-scm.com/download/win
2. Ou use GitHub Desktop: https://desktop.github.com/

### Problema: Conflitos ao fazer Pull

**Solução**:

1. **No GitHub Desktop:**
   - Vá em `Repository` → `Pull`
   - Se houver conflitos, o GitHub Desktop mostrará opções
   - Escolha qual versão manter ou mescle manualmente

2. **Via Terminal:**
   ```bash
   git pull origin main
   # Se houver conflitos, resolva manualmente nos arquivos
   git add .
   git commit -m "Resolve conflitos"
   git push origin main
   ```

### Problema: Sistema não inicia

**Solução**:

1. **Verificar se Python está instalado:**
   ```powershell
   python --version
   ```

2. **Verificar se dependências estão instaladas:**
   ```powershell
   pip list
   ```

3. **Reinstalar dependências:**
   ```powershell
   pip install -r requirements.txt --upgrade
   ```

4. **Verificar migrações:**
   ```powershell
   python manage.py migrate
   ```

### Problema: Banco de dados corrompido

**Solução**:

1. **Fazer backup:**
   ```powershell
   copy db.sqlite3 db.sqlite3.backup
   ```

2. **Recriar banco:**
   ```powershell
   del db.sqlite3
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## 📂 **Estrutura Importante da Pasta**

```
Monpec_GestaoRural/
├── manage.py                 # Script principal do Django
├── requirements.txt          # Dependências Python
├── db.sqlite3               # Banco de dados (não vai para Git)
├── sistema_rural/           # Configurações do Django
│   └── settings.py
├── gestao_rural/            # App principal
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── static/                  # Arquivos estáticos (CSS, JS, imagens)
├── templates/               # Templates HTML
└── media/                   # Uploads de usuários (não vai para Git)
```

---

## 🔐 **Arquivos que NÃO vão para o GitHub**

Estes arquivos estão no `.gitignore` e não serão sincronizados:

- `db.sqlite3` - Banco de dados local
- `*.pyc` - Arquivos compilados Python
- `__pycache__/` - Cache Python
- `venv/` - Ambiente virtual (se criar)
- `media/` - Uploads de usuários
- `*.log` - Logs do sistema

**⚠️ Importante**: Nunca commite senhas, chaves de API ou dados sensíveis!

---

## 🎯 **Checklist Diário**

- [ ] Fazer Pull no início do dia
- [ ] Ativar ambiente virtual (se usar)
- [ ] Iniciar servidor e testar
- [ ] Fazer alterações
- [ ] Testar alterações localmente
- [ ] Fazer Commit com mensagem descritiva
- [ ] Fazer Push para GitHub
- [ ] Verificar que Push foi bem-sucedido

---

## 📞 **Precisa de Ajuda?**

1. **Verifique os logs do Django:**
   - Erros aparecem no terminal onde o servidor está rodando

2. **Verifique o GitHub Desktop:**
   - Aba "History" mostra todos os commits
   - Aba "Changes" mostra alterações pendentes

3. **Documentação Django:**
   - https://docs.djangoproject.com/

---

## 🚀 **Próximos Passos**

Agora que você sabe como trabalhar com a pasta sincronizada:

1. ✅ Configure seu ambiente
2. ✅ Inicie o sistema
3. ✅ Faça suas alterações
4. ✅ Mantenha tudo sincronizado com GitHub

**Bom trabalho! 🎉**


