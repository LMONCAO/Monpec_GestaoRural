# Script para Configurar Envio Real de E-mails no MONPEC
# Execute este script na raiz do projeto

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR ENVIO REAL DE E-MAILS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se arquivo .env já existe
$envFile = ".env"
$envExists = Test-Path $envFile

if ($envExists) {
    Write-Host "⚠️  Arquivo .env já existe!" -ForegroundColor Yellow
    $sobrescrever = Read-Host "Deseja adicionar configurações de e-mail? (S/N)"
    if ($sobrescrever -ne "S" -and $sobrescrever -ne "s") {
        Write-Host "Operação cancelada." -ForegroundColor Red
        exit
    }
} else {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Green
}

Write-Host ""
Write-Host "Escolha o provedor de e-mail:" -ForegroundColor Cyan
Write-Host "1. Gmail (Recomendado)"
Write-Host "2. Outlook/Hotmail"
Write-Host "3. Yahoo Mail"
Write-Host "4. Servidor SMTP Personalizado"
Write-Host ""

$opcao = Read-Host "Digite o número da opção (1-4)"

$emailBackend = "django.core.mail.backends.smtp.EmailBackend"
$emailPort = "587"
$emailUseTLS = "True"
$emailHost = ""
$defaultFromEmail = ""

switch ($opcao) {
    "1" {
        $emailHost = "smtp.gmail.com"
        Write-Host ""
        Write-Host "⚠️  IMPORTANTE: Para Gmail, você precisa usar uma SENHA DE APP!" -ForegroundColor Yellow
        Write-Host "   Acesse: https://myaccount.google.com/apppasswords" -ForegroundColor Yellow
        Write-Host "   Gere uma senha de app e use ela abaixo." -ForegroundColor Yellow
        Write-Host ""
        $emailUser = Read-Host "Digite seu e-mail Gmail (ex: seu-email@gmail.com)"
        $emailPassword = Read-Host "Digite a Senha de App do Gmail (16 caracteres)" -AsSecureString
        $emailPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPassword)
        )
        $defaultFromEmail = $emailUser
    }
    "2" {
        $emailHost = "smtp-mail.outlook.com"
        $emailUser = Read-Host "Digite seu e-mail Outlook (ex: seu-email@outlook.com)"
        $emailPassword = Read-Host "Digite sua senha" -AsSecureString
        $emailPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPassword)
        )
        $defaultFromEmail = $emailUser
    }
    "3" {
        $emailHost = "smtp.mail.yahoo.com"
        Write-Host ""
        Write-Host "⚠️  Para Yahoo, você pode precisar de uma Senha de App!" -ForegroundColor Yellow
        Write-Host ""
        $emailUser = Read-Host "Digite seu e-mail Yahoo (ex: seu-email@yahoo.com)"
        $emailPassword = Read-Host "Digite sua senha ou Senha de App" -AsSecureString
        $emailPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPassword)
        )
        $defaultFromEmail = $emailUser
    }
    "4" {
        $emailHost = Read-Host "Digite o servidor SMTP (ex: mail.seudominio.com.br)"
        $emailPort = Read-Host "Digite a porta (padrão: 587)"
        if ([string]::IsNullOrWhiteSpace($emailPort)) {
            $emailPort = "587"
        }
        $emailUser = Read-Host "Digite o usuário SMTP (ex: noreply@seudominio.com.br)"
        $emailPassword = Read-Host "Digite a senha" -AsSecureString
        $emailPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPassword)
        )
        $defaultFromEmail = Read-Host "Digite o e-mail remetente (ex: noreply@seudominio.com.br)"
    }
    default {
        Write-Host "Opção inválida!" -ForegroundColor Red
        exit
    }
}

# Solicitar URL do site
Write-Host ""
$siteUrl = Read-Host "Digite a URL do site (ex: http://localhost:8000 ou https://seudominio.com.br)"

# Criar conteúdo do .env
$envContent = @"
# Configuração de E-mail - Gerado automaticamente
EMAIL_BACKEND=$emailBackend
EMAIL_HOST=$emailHost
EMAIL_PORT=$emailPort
EMAIL_USE_TLS=$emailUseTLS
EMAIL_HOST_USER=$emailUser
EMAIL_HOST_PASSWORD=$emailPasswordPlain
DEFAULT_FROM_EMAIL=$defaultFromEmail
SITE_URL=$siteUrl
"@

# Adicionar ao .env existente ou criar novo
if ($envExists) {
    # Verificar se já tem configurações de e-mail
    $envContentAtual = Get-Content $envFile -Raw
    if ($envContentAtual -match "EMAIL_BACKEND") {
        Write-Host ""
        Write-Host "⚠️  O arquivo .env já contém configurações de e-mail!" -ForegroundColor Yellow
        $substituir = Read-Host "Deseja substituir? (S/N)"
        if ($substituir -eq "S" -or $substituir -eq "s") {
            # Remover linhas antigas de e-mail
            $linhas = Get-Content $envFile | Where-Object { 
                $_ -notmatch "^EMAIL_" -and $_ -notmatch "^DEFAULT_FROM_EMAIL" -and $_ -notmatch "^SITE_URL"
            }
            $linhas + $envContent | Set-Content $envFile
            Write-Host "✅ Configurações de e-mail atualizadas!" -ForegroundColor Green
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Red
            exit
        }
    } else {
        Add-Content -Path $envFile -Value "`n$envContent"
        Write-Host "✅ Configurações de e-mail adicionadas ao .env!" -ForegroundColor Green
    }
} else {
    Set-Content -Path $envFile -Value $envContent
    Write-Host "✅ Arquivo .env criado com sucesso!" -ForegroundColor Green
}

# Verificar se .env está no .gitignore
$gitignore = ".gitignore"
if (Test-Path $gitignore) {
    $gitignoreContent = Get-Content $gitignore -Raw
    if ($gitignoreContent -notmatch "\.env") {
        Add-Content -Path $gitignore -Value "`n# Arquivo de configuração local`n.env"
        Write-Host "✅ Arquivo .env adicionado ao .gitignore!" -ForegroundColor Green
    }
} else {
    Set-Content -Path $gitignore -Value "# Arquivo de configuração local`n.env"
    Write-Host "✅ Arquivo .gitignore criado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Reinicie o servidor Django" -ForegroundColor White
Write-Host "2. Teste o envio de e-mail em: http://localhost:8000/recuperar-senha/" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   - Para Gmail, certifique-se de usar uma Senha de App" -ForegroundColor White
Write-Host "   - Verifique a pasta de spam se o e-mail não chegar" -ForegroundColor White
Write-Host "   - O arquivo .env contém senhas - NÃO commite no Git!" -ForegroundColor White
Write-Host ""
Write-Host "📖 Para mais informações, consulte: COMO_CONFIGURAR_EMAIL_REAL.md" -ForegroundColor Cyan
Write-Host ""


