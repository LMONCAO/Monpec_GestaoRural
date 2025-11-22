# 🚀 INÍCIO RÁPIDO - Publicar Site

## ⚡ Resumo do Processo (30-45 minutos)

### **1. Preparar Código no GitHub** ✅
```powershell
git add .
git commit -m "Preparar para deploy"
git push origin main
```

### **2. Instalar Google Cloud SDK** 📥
- Baixe: https://cloud.google.com/sdk/docs/install
- Ou: `choco install gcloudsdk` (se tiver Chocolatey)

### **3. Configurar Google Cloud** ⚙️
1. Acesse: https://console.cloud.google.com
2. Crie projeto: `monpec-sistema-rural`
3. Habilite faturamento
4. Habilite APIs: Cloud Run, Cloud SQL, Cloud Build

### **4. Executar Script de Publicação** 🚀
```powershell
# No PowerShell, na pasta do projeto
.\PUBLICAR_SITE.ps1
```

Este script irá:
- ✅ Criar banco de dados PostgreSQL
- ✅ Fazer build da aplicação
- ✅ Fazer deploy no Cloud Run
- ✅ Configurar variáveis de ambiente

### **5. Executar Migrações** 🔄
```powershell
.\EXECUTAR_MIGRACOES.ps1
```

### **6. Criar Superusuário** 👤
```powershell
.\CRIAR_SUPERUSUARIO.ps1
```

### **7. Configurar Domínio** 🌐
Siga as instruções em: `CONFIGURAR_DOMINIO.md`

## 📋 Checklist Completo

- [ ] Código no GitHub
- [ ] Google Cloud SDK instalado
- [ ] Projeto criado no Google Cloud
- [ ] Faturamento habilitado
- [ ] APIs habilitadas
- [ ] Script `PUBLICAR_SITE.ps1` executado
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Domínio configurado
- [ ] DNS propagado
- [ ] Site acessível em monpec.com.br

## 🆘 Precisa de Ajuda?

Consulte o guia completo: `GUIA_PUBLICACAO_COMPLETO.md`

## 💰 Custos

- **Estimativa inicial:** ~$10-20/mês
- **Crédito grátis:** $300 por 90 dias (novos usuários)

## ✅ Pronto!

Após completar todos os passos, seu site estará em:
**https://monpec.com.br**


