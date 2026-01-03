# 🚀 Instalar PostgreSQL Agora - Guia Rápido

## Opção 1: Download Direto (Mais Rápido - 5 minutos)

### Passo 1: Baixar
1. Acesse: **https://www.postgresql.org/download/windows/**
2. Clique em **"Download the installer"**
3. Baixe a versão mais recente (recomendado: PostgreSQL 15 ou 16)

### Passo 2: Instalar
1. Execute o instalador baixado
2. **Próximo** → **Próximo** → **Próximo**
3. **Localização**: Deixe padrão (`C:\Program Files\PostgreSQL\...`)
4. **Componentes**: Deixe tudo marcado (padrão)
5. **Data Directory**: Deixe padrão
6. **Senha**: Digite `postgres` (ou anote a senha que escolher)
7. **Porta**: Deixe `5432` (padrão)
8. **Locale**: Deixe padrão
9. **Próximo** → **Próximo** → **Instalar**
10. Aguarde a instalação (2-5 minutos)
11. **Finalizar**

### Passo 3: Verificar
O PostgreSQL deve iniciar automaticamente. Para verificar:

```powershell
Get-Service -Name "*postgresql*"
```

Se aparecer "Running", está OK!

### Passo 4: Executar Script
```powershell
python criar_banco_e_migrar.py
```

**Pronto!** ✅

---

## Opção 2: Via Chocolatey (Requer Admin)

### Abra PowerShell como Administrador:
1. Clique com botão direito no PowerShell
2. Selecione **"Executar como administrador"**

### Execute:
```powershell
choco install postgresql --params '/Password:postgres' -y
```

### Aguarde instalação e execute:
```powershell
python criar_banco_e_migrar.py
```

---

## ⚠️ Se a Senha for Diferente

Se você usou uma senha diferente de `postgres`, edite o arquivo `.env`:

```env
DB_PASSWORD=sua_senha_aqui
```

---

## ✅ Após Instalar

Execute apenas este comando:

```powershell
python criar_banco_e_migrar.py
```

Isso irá:
- ✅ Criar o banco `monpec_db_local`
- ✅ Aplicar todas as 90 migrações
- ✅ Criar todas as tabelas
- ✅ Verificar se tudo está OK

---

## 🔍 Verificar se Funcionou

```powershell
# Ver migrações
python manage.py showmigrations

# Testar conexão
python manage.py dbshell
# Digite: \dt (para ver tabelas)
# Digite: \q (para sair)
```

---

## ❓ Problemas Comuns

### "Connection refused"
- **Solução**: Inicie o serviço PostgreSQL:
  ```powershell
  Start-Service postgresql-x64-*
  ```

### "Password authentication failed"
- **Solução**: Verifique a senha no arquivo `.env`

### "Database does not exist"
- **Solução**: O script cria automaticamente, mas se falhar:
  ```sql
  CREATE DATABASE monpec_db_local;
  ```

---

**Tempo estimado**: 5-10 minutos  
**Dificuldade**: Fácil  
**Resultado**: Banco configurado e todas as migrações aplicadas! 🎉

