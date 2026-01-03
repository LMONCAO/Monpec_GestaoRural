# 🚀 Instruções de Deploy Completo - Sistema MONPEC

## ✅ Status Atual
- ✅ Erro de sintaxe corrigido em `views_pecuaria_completa.py`
- ✅ Sistema funcionando no localhost
- ⚠️ Migrações pendentes precisam ser aplicadas

## 📋 Passos para Deploy Completo

### 1. Navegue até o diretório do projeto

Abra o PowerShell ou Terminal no diretório:
```
C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural
```

### 2. Execute o Script de Deploy Simplificado

**Opção A: Script Simples (Recomendado)**
```powershell
.\DEPLOY_AGORA_SIMPLES.ps1
```

**Opção B: Comandos Manuais**

```powershell
# 1. Aplicar migrações
python manage.py migrate --noinput

# 2. Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear

# 3. Verificar sistema
python manage.py check
```

### 3. Verificar se tudo está OK

O sistema deve mostrar:
- ✅ Migrações aplicadas
- ✅ Arquivos estáticos coletados
- ✅ Sem erros no sistema

### 4. Testar o Sistema

**Modo Desenvolvimento (Localhost):**
```powershell
python manage.py runserver
```

Acesse: http://localhost:8000

**Modo Produção:**

Se você tem um servidor de produção configurado, use:
```powershell
# Com configurações de produção
python manage.py runserver --settings=sistema_rural.settings_producao
```

## 🔧 Scripts Disponíveis

1. **DEPLOY_AGORA_SIMPLES.ps1** - Deploy rápido e simples
2. **DEPLOY_COMPLETO_PRODUCAO.ps1** - Deploy completo com verificações extras

## ⚠️ Importante

- Certifique-se de estar no diretório correto (onde está o `manage.py`)
- O sistema está configurado para usar `sistema_rural.settings` por padrão (desenvolvimento)
- Para produção, configure as variáveis de ambiente ou use `settings_producao`

## 📝 Próximos Passos

Após aplicar as migrações e coletar os arquivos estáticos:

1. ✅ Sistema pronto para uso em desenvolvimento
2. ✅ Teste todas as funcionalidades
3. ✅ Configure produção se necessário
4. ✅ Deploy no servidor de produção (se aplicável)

## 🆘 Troubleshooting

**Erro: "No module named 'django'"**
```powershell
pip install -r requirements.txt
```

**Erro: "manage.py não encontrado"**
- Certifique-se de estar no diretório raiz do projeto

**Erro ao coletar arquivos estáticos**
- Normal se não houver arquivos estáticos customizados
- Verifique se a pasta `staticfiles` foi criada
