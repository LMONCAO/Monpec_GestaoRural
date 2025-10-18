# 🚀 Deploy do Sistema Rural com GitHub + Vercel

## 📋 Configuração para Deploy Automático

### 1. Configurar Repositório GitHub
```bash
# Inicializar repositório Git
git init
git add .
git commit -m "Sistema Rural - Deploy inicial"

# Conectar ao GitHub
git remote add origin https://github.com/SEU_USUARIO/sistema-rural.git
git push -u origin main
```

### 2. Configurar Vercel
1. Acesse: https://vercel.com
2. Conecte sua conta GitHub
3. Importe o repositório `sistema-rural`
4. Configure o domínio: `monpec.com.br`

### 3. Configurar Domínio
1. No painel do Vercel, vá em "Domains"
2. Adicione `monpec.com.br`
3. Configure os DNS records no seu provedor de domínio

### 4. Variáveis de Ambiente
Configure no Vercel:
```
DJANGO_SETTINGS_MODULE=sistema_rural.settings
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=monpec.com.br,*.vercel.app
```

## 🌐 URLs de Acesso
- **Produção**: https://monpec.com.br
- **Vercel**: https://sistema-rural.vercel.app

## ✅ Vantagens
- ✅ Deploy automático
- ✅ HTTPS automático
- ✅ CDN global
- ✅ Backup automático
- ✅ Sem problemas de conectividade
- ✅ Domínio próprio

## 🔧 Comandos Úteis
```bash
# Fazer deploy manual
git add .
git commit -m "Atualização do sistema"
git push origin main

# Ver logs do Vercel
vercel logs
```


