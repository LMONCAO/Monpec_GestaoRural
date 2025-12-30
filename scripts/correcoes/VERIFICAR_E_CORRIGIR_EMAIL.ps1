# Script para verificar e corrigir configuração de e-mail
# Execute: .\VERIFICAR_E_CORRIGIR_EMAIL.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  VERIFICAÇÃO DE CONFIGURAÇÃO DE E-MAIL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$envFile = ".env"
$envExists = Test-Path $envFile

# Verificar se .env existe
if ($envExists) {
    Write-Host "✅ Arquivo .env encontrado!" -ForegroundColor Green
    Write-Host ""
    
    # Ler conteúdo
    $conteudo = Get-Content $envFile -Raw
    
    # Verificar se tem EMAIL_BACKEND
    if ($conteudo -match "EMAIL_BACKEND") {
        if ($conteudo -match "console\.EmailBackend") {
            Write-Host "❌ PROBLEMA ENCONTRADO!" -ForegroundColor Red
            Write-Host "   O arquivo .env está usando backend de CONSOLE" -ForegroundColor Yellow
            Write-Host "   Os e-mails não estão sendo enviados de verdade!" -ForegroundColor Yellow
            Write-Host ""
            
            $corrigir = Read-Host "Deseja corrigir automaticamente? (S/N)"
            if ($corrigir -eq "S" -or $corrigir -eq "s") {
                # Substituir console por smtp
                $conteudo = $conteudo -replace "django\.core\.mail\.backends\.console\.EmailBackend", "django.core.mail.backends.smtp.EmailBackend"
                Set-Content -Path $envFile -Value $conteudo
                Write-Host "✅ Arquivo .env corrigido!" -ForegroundColor Green
            }
        } elseif ($conteudo -match "smtp\.EmailBackend") {
            Write-Host "✅ Backend SMTP configurado corretamente!" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  Arquivo .env não contém EMAIL_BACKEND" -ForegroundColor Yellow
        Write-Host "   Adicionando configurações de e-mail..." -ForegroundColor Yellow
        
        $adicionar = Read-Host "Deseja adicionar configurações de e-mail? (S/N)"
        if ($adicionar -eq "S" -or $adicionar -eq "s") {
            Add-Content -Path $envFile -Value "`n# Configuração de E-mail`nEMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`nEMAIL_HOST=smtp.gmail.com`nEMAIL_PORT=587`nEMAIL_USE_TLS=True`nEMAIL_HOST_USER=`nEMAIL_HOST_PASSWORD=`nDEFAULT_FROM_EMAIL=`nSITE_URL=http://localhost:8000"
            Write-Host "✅ Configurações adicionadas! Configure EMAIL_HOST_USER e EMAIL_HOST_PASSWORD" -ForegroundColor Green
        }
    }
    
    # Verificar se tem credenciais
    if ($conteudo -match "EMAIL_HOST_USER" -and $conteudo -notmatch "EMAIL_HOST_USER=$") {
        Write-Host "✅ EMAIL_HOST_USER configurado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  EMAIL_HOST_USER não configurado ou vazio" -ForegroundColor Yellow
    }
    
    if ($conteudo -match "EMAIL_HOST_PASSWORD" -and $conteudo -notmatch "EMAIL_HOST_PASSWORD=$") {
        Write-Host "✅ EMAIL_HOST_PASSWORD configurado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  EMAIL_HOST_PASSWORD não configurado ou vazio" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Arquivo .env NÃO encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "   O sistema está usando valores padrão do settings.py" -ForegroundColor Yellow
    Write-Host "   Isso significa que está usando backend de CONSOLE!" -ForegroundColor Yellow
    Write-Host "   Os e-mails não estão sendo enviados de verdade!" -ForegroundColor Yellow
    Write-Host ""
    
    $criar = Read-Host "Deseja criar o arquivo .env agora? (S/N)"
    if ($criar -eq "S" -or $criar -eq "s") {
        Write-Host ""
        Write-Host "Escolha o provedor de e-mail:" -ForegroundColor Cyan
        Write-Host "1. Gmail (Recomendado)"
        Write-Host "2. Outlook/Hotmail"
        Write-Host "3. Criar arquivo vazio para configurar depois"
        Write-Host ""
        
        $opcao = Read-Host "Digite o número (1-3)"
        
        switch ($opcao) {
            "1" {
                $email = Read-Host "Digite seu e-mail Gmail"
                Write-Host ""
                Write-Host "⚠️  Para Gmail, você precisa usar uma SENHA DE APP!" -ForegroundColor Yellow
                Write-Host "   Acesse: https://myaccount.google.com/apppasswords" -ForegroundColor Yellow
                Write-Host ""
                $senha = Read-Host "Digite a Senha de App" -AsSecureString
                $senhaPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senha)
                )
                
                $conteudo = @"
# Configuração de E-mail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$email
EMAIL_HOST_PASSWORD=$senhaPlain
DEFAULT_FROM_EMAIL=$email
SITE_URL=http://localhost:8000
"@
                Set-Content -Path $envFile -Value $conteudo
                Write-Host ""
                Write-Host "✅ Arquivo .env criado com configurações do Gmail!" -ForegroundColor Green
            }
            "2" {
                $email = Read-Host "Digite seu e-mail Outlook"
                $senha = Read-Host "Digite sua senha" -AsSecureString
                $senhaPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senha)
                )
                
                $conteudo = @"
# Configuração de E-mail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$email
EMAIL_HOST_PASSWORD=$senhaPlain
DEFAULT_FROM_EMAIL=$email
SITE_URL=http://localhost:8000
"@
                Set-Content -Path $envFile -Value $conteudo
                Write-Host ""
                Write-Host "✅ Arquivo .env criado com configurações do Outlook!" -ForegroundColor Green
            }
            "3" {
                $conteudo = @"
# Configuração de E-mail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
SITE_URL=http://localhost:8000
"@
                Set-Content -Path $envFile -Value $conteudo
                Write-Host ""
                Write-Host "✅ Arquivo .env criado! Configure as variáveis acima." -ForegroundColor Green
            }
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. REINICIE o servidor Django (Ctrl+C e depois python manage.py runserver)" -ForegroundColor White
Write-Host "2. Execute: python testar_email.py" -ForegroundColor White
Write-Host "3. Ou teste pela interface: http://localhost:8000/recuperar-senha/" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Sempre reinicie o servidor após alterar o .env!" -ForegroundColor Yellow
Write-Host ""


