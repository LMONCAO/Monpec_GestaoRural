# 🚀 COMO INICIAR O SERVIDOR

## Método 1: Script Batch (Windows - Recomendado)

Simplesmente execute o arquivo `INICIAR.bat` na raiz do projeto:

```batch
INICIAR.bat
```

Este script irá:
1. ✅ Verificar se o Python está instalado
2. ✅ Executar as migrações do banco de dados
3. ✅ Iniciar o servidor Django na porta 8000

## Método 2: Comando Direto

No terminal/PowerShell, execute:

```bash
python manage.py runserver 0.0.0.0:8000
```

## Método 3: Script de Manutenção

Use o script organizado em `scripts/manutencao/`:

```batch
scripts\manutencao\INICIAR.bat
```

---

## 🌐 Acessar o Sistema

Após iniciar o servidor, acesse:

- **Local:** http://localhost:8000
- **Rede local:** http://SEU_IP:8000
- **Todos os IPs:** O servidor está configurado para aceitar conexões de qualquer IP (0.0.0.0:8000)

---

## ⚠️ Requisitos

1. **Python 3.11+** instalado e no PATH
2. **Dependências instaladas:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Banco de dados configurado:**
   ```bash
   python manage.py migrate
   ```

---

## 🛑 Parar o Servidor

Pressione `Ctrl+C` no terminal onde o servidor está rodando.

---

## 🔧 Solução de Problemas

### Erro: "Python não encontrado"
- Instale Python 3.11+ do site oficial
- Certifique-se de adicionar Python ao PATH durante a instalação

### Erro: "No module named 'django'"
- Execute: `pip install -r requirements.txt`

### Erro: "Port 8000 already in use"
- Pare outros processos usando a porta 8000
- Ou use outra porta: `python manage.py runserver 0.0.0.0:8001`

### Erro de migrações
- Execute: `python manage.py migrate`

---

## 📝 Notas

- O servidor está configurado para aceitar conexões de qualquer IP (`0.0.0.0`)
- Isso permite acesso via celular/outros dispositivos na mesma rede
- Para produção, use um servidor WSGI como Gunicorn ou uWSGI

---

**Servidor iniciado com sucesso! 🎉**



















