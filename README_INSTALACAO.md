# Guia de Instalação - MONPEC Gestão Rural

Este guia fornece instruções detalhadas para instalação do sistema MONPEC.

## 📋 Pré-requisitos

### Windows

- Windows 10 ou superior
- Python 3.11 ou superior
  - Opção 1: Instalar Python do site oficial (https://www.python.org/downloads/)
  - Opção 2: Usar Python portátil na pasta `python311`
- Git (opcional, para atualizações do GitHub)

### Linux/Mac

- Python 3.11 ou superior
- pip (geralmente vem com Python)
- Git (opcional, para atualizações do GitHub)

## 🚀 Instalação Passo a Passo

### Opção 1: Instalação Automática (Recomendado)

#### Windows

1. Abra o prompt de comando ou PowerShell
2. Navegue até a pasta do projeto:
   ```batch
   cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
   ```
3. Execute o instalador:
   ```batch
   INSTALAR.bat
   ```

#### Linux/Mac

1. Abra o terminal
2. Navegue até a pasta do projeto:
   ```bash
   cd /caminho/para/Monpec_GestaoRural
   ```
3. Dê permissão de execução:
   ```bash
   chmod +x INSTALAR.sh
   ```
4. Execute o instalador:
   ```bash
   ./INSTALAR.sh
   ```

### Opção 2: Instalação Manual

#### 1. Instalar Dependências

**Windows:**
```batch
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

#### 2. Aplicar Migrações

```batch
python manage.py migrate
```

**Linux/Mac:**
```bash
python3 manage.py migrate
```

#### 3. Criar Superusuário

```batch
python manage.py createsuperuser
```

**Linux/Mac:**
```bash
python3 manage.py createsuperuser
```

#### 4. Coletar Arquivos Estáticos

```batch
python manage.py collectstatic
```

**Linux/Mac:**
```bash
python3 manage.py collectstatic
```

## 🔄 Atualização do Sistema

### Atualizar do GitHub

#### Windows

```batch
ATUALIZAR_GITHUB.bat
```

#### Linux/Mac

```bash
chmod +x ATUALIZAR_GITHUB.sh
./ATUALIZAR_GITHUB.sh
```

### Atualizar e Iniciar Automaticamente

#### Windows

```batch
ATUALIZAR_E_INICIAR.bat
```

#### Linux/Mac

```bash
chmod +x ATUALIZAR_E_INICIAR.sh
./ATUALIZAR_E_INICIAR.sh
```

## 🎯 Primeiro Uso

1. **Iniciar o servidor:**
   - Windows: `INICIAR.bat`
   - Linux/Mac: `./INICIAR.sh`

2. **Acessar o sistema:**
   - Abra o navegador em: `http://localhost:8000`

3. **Fazer login:**
   - Usuário: `admin`
   - Senha: `admin`

4. **Alterar senha:**
   - Após o primeiro login, vá em Configurações > Alterar Senha

## ⚙️ Configurações Adicionais

### Configurar Banco Marcelo Sanguino

Se você precisa usar o banco do Marcelo Sanguino:

```batch
python configurar_banco_marcelo_sanguino.py
```

### Verificar Instalação

```batch
python manage.py check
```

### Verificar Banco de Dados

```batch
python verificar_banco_correto.py
```

## 🐛 Solução de Problemas

### Erro: Python não encontrado

**Solução:**
- Instale o Python 3.11 ou superior
- Ou coloque o Python portátil na pasta `python311`

### Erro: Módulo não encontrado

**Solução:**
```batch
python -m pip install -r requirements.txt
```

### Erro: Migrações falhando

**Solução:**
```batch
python manage.py migrate --run-syncdb
```

### Erro: Porta 8000 já em uso

**Solução:**
- Pare outros processos Python
- Ou use outra porta: `python manage.py runserver 0.0.0.0:8001`

## 📚 Próximos Passos

Após a instalação, consulte:
- [Início Rápido](QUICK_START.md) - Para começar a usar o sistema
- [Configuração de Banco de Dados](CONFIGURACAO_BANCO_DADOS.md) - Para configurar banco remoto






















