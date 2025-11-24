# Script para Verificar e Diagnosticar Configuração de DNS do monpec.com.br
# Para Google Cloud Run

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 DIAGNÓSTICO DE DNS - monpec.com.br" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Host "[1/5] Verificando gcloud CLI..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✅ gcloud encontrado: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud não encontrado. Instale primeiro:" -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Verificar autenticação
Write-Host "[2/5] Verificando autenticação..." -ForegroundColor Yellow
try {
    $currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    if ($currentAccount) {
        Write-Host "✅ Autenticado como: $currentAccount" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Não autenticado. Execute: gcloud auth login" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao verificar autenticação" -ForegroundColor Yellow
}

Write-Host ""

# Verificar projeto
Write-Host "[3/5] Verificando projeto atual..." -ForegroundColor Yellow
try {
    $currentProject = gcloud config get-value project 2>&1
    if ($currentProject -and $currentProject -notmatch "ERROR") {
        Write-Host "✅ Projeto atual: $currentProject" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Nenhum projeto configurado. Configure com:" -ForegroundColor Yellow
        Write-Host "   gcloud config set project monpec-sistema-rural" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️  Erro ao verificar projeto" -ForegroundColor Yellow
}

Write-Host ""

# Verificar mapeamento de domínio no Cloud Run
Write-Host "[4/5] Verificando mapeamento de domínio no Cloud Run..." -ForegroundColor Yellow
Write-Host ""
try {
    $domainMapping = gcloud run domain-mappings describe monpec.com.br --region us-central1 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Domínio mapeado no Cloud Run!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Informações do mapeamento:" -ForegroundColor Cyan
        Write-Host $domainMapping
        Write-Host ""
        
        # Extrair registros DNS necessários
        Write-Host "🔍 Procurando registros DNS necessários..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "⚠️  IMPORTANTE: Você precisa adicionar os registros DNS abaixo no Registro.br" -ForegroundColor Yellow
        Write-Host ""
        
        # Tentar obter os registros DNS
        $dnsRecords = gcloud run domain-mappings describe monpec.com.br --region us-central1 --format="value(status.resourceRecords)" 2>&1
        
        if ($dnsRecords) {
            Write-Host "📋 Registros DNS que você precisa adicionar no Registro.br:" -ForegroundColor Cyan
            Write-Host $dnsRecords
        } else {
            Write-Host "💡 Para ver os registros DNS, execute:" -ForegroundColor Yellow
            Write-Host "   gcloud run domain-mappings describe monpec.com.br --region us-central1" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "❌ Domínio NÃO está mapeado no Cloud Run!" -ForegroundColor Red
        Write-Host ""
        Write-Host "📝 Para mapear o domínio, execute:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   gcloud run domain-mappings create \" -ForegroundColor Cyan
        Write-Host "       --service monpec \" -ForegroundColor Cyan
        Write-Host "       --domain monpec.com.br \" -ForegroundColor Cyan
        Write-Host "       --region us-central1" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  Depois de mapear, o Google Cloud vai mostrar os registros DNS" -ForegroundColor Yellow
        Write-Host "   que você precisa adicionar no Registro.br!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro ao verificar mapeamento de domínio" -ForegroundColor Red
    Write-Host "   Certifique-se de que o serviço 'monpec' existe no Cloud Run" -ForegroundColor Yellow
}

Write-Host ""

# Verificar propagação DNS
Write-Host "[5/5] Verificando propagação DNS..." -ForegroundColor Yellow
Write-Host ""
try {
    $nslookup = nslookup monpec.com.br 2>&1
    if ($nslookup -match "Name:") {
        Write-Host "✅ DNS resolvendo para monpec.com.br" -ForegroundColor Green
        Write-Host $nslookup
    } else {
        Write-Host "⚠️  DNS ainda não propagado ou não configurado" -ForegroundColor Yellow
        Write-Host "   Aguarde 15 minutos - 2 horas após configurar no Registro.br" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar DNS (pode ser normal se ainda não configurou)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📚 PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Se o domínio NÃO está mapeado:" -ForegroundColor Yellow
Write-Host "   → Execute o comando de mapeamento acima" -ForegroundColor White
Write-Host "   → Anote os registros DNS que o Google mostrar" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Se o domínio JÁ está mapeado:" -ForegroundColor Yellow
Write-Host "   → Acesse o painel do Registro.br" -ForegroundColor White
Write-Host "   → Vá em 'Zona DNS' ou 'Registros DNS'" -ForegroundColor White
Write-Host "   → Adicione os registros A e CNAME fornecidos pelo Google Cloud" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  No Registro.br, você precisa:" -ForegroundColor Yellow
Write-Host "   → Ativar 'DNS Hosting' ou 'Zona DNS' (se ainda não ativou)" -ForegroundColor White
Write-Host "   → Adicionar registro tipo A com o IP fornecido pelo Google" -ForegroundColor White
Write-Host "   → Adicionar registro tipo CNAME para www (se fornecido)" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Aguardar propagação:" -ForegroundColor Yellow
Write-Host "   → 15 minutos a 2 horas (geralmente menos de 1 hora)" -ForegroundColor White
Write-Host "   → Verifique em: https://dnschecker.org" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Testar acesso:" -ForegroundColor Yellow
Write-Host "   → https://monpec.com.br" -ForegroundColor White
Write-Host "   → SSL pode levar até 24 horas para aparecer" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentação completa:" -ForegroundColor Cyan
Write-Host "   → CONFIGURAR_DOMINIO_REGISTRO_BR.md" -ForegroundColor White
Write-Host "   → CONFIGURAR_DOMINIO_PASSO_A_PASSO.md" -ForegroundColor White
Write-Host ""












