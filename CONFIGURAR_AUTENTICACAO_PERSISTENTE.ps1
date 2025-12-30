# Configurar Autenticação Persistente - Google Cloud
# Não pede senha toda hora

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR AUTENTICACAO PERSISTENTE" -ForegroundColor Cyan
Write-Host "  Google Cloud - Nao pede senha toda hora" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"

Write-Host "[INFO] Este script vai configurar a autenticacao persistente" -ForegroundColor Yellow
Write-Host "[INFO] Voce so precisara fazer login UMA VEZ" -ForegroundColor Yellow
Write-Host "[INFO] Depois disso, os scripts funcionarao automaticamente" -ForegroundColor Yellow
Write-Host ""

# Verificar gcloud
Write-Host "[1/4] Verificando Google Cloud SDK..." -ForegroundColor Cyan
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "[ERRO] gcloud nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Baixe e instale o Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Google Cloud SDK encontrado" -ForegroundColor Green
Write-Host ""

# Configurar autenticação principal
Write-Host "[2/4] Configurando autenticacao principal..." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Isso vai abrir o navegador para fazer login" -ForegroundColor Yellow
Write-Host "Voce so precisa fazer isso UMA VEZ" -ForegroundColor Yellow
Write-Host ""
Read-Host "Pressione Enter para continuar"

$result = gcloud auth login --no-launch-browser 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha na autenticacao principal!" -ForegroundColor Red
    Write-Host "Tente novamente ou execute: gcloud auth login" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Autenticacao principal configurada" -ForegroundColor Green
Write-Host ""

# Configurar Application Default Credentials
Write-Host "[3/4] Configurando credenciais padrao (Application Default Credentials)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Isso vai abrir o navegador novamente" -ForegroundColor Yellow
Write-Host "Voce so precisa fazer isso UMA VEZ" -ForegroundColor Yellow
Write-Host ""
Read-Host "Pressione Enter para continuar"

$result = gcloud auth application-default login --no-launch-browser 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha na configuracao de credenciais padrao!" -ForegroundColor Red
    Write-Host "Tente novamente ou execute: gcloud auth application-default login" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Credenciais padrao configuradas" -ForegroundColor Green
Write-Host ""

# Configurar projeto
Write-Host "[4/4] Configurando projeto padrao..." -ForegroundColor Cyan
$result = gcloud config set project $PROJECT_ID 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha ao configurar projeto!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Projeto configurado: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Verificar configuração
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO CONFIGURACAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Contas autenticadas:" -ForegroundColor Yellow
gcloud auth list
Write-Host ""

Write-Host "Projeto atual:" -ForegroundColor Yellow
gcloud config get-value project
Write-Host ""

Write-Host "Verificando credenciais padrao:" -ForegroundColor Yellow
$tokenCheck = gcloud auth application-default print-access-token 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[AVISO] Credenciais padrao podem nao estar funcionando" -ForegroundColor Yellow
    Write-Host "Tente executar: gcloud auth application-default login" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Credenciais padrao funcionando corretamente" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[SUCESSO] Autenticacao persistente configurada!" -ForegroundColor Green
Write-Host ""
Write-Host "Agora voce pode:" -ForegroundColor Yellow
Write-Host "- Executar scripts de deploy sem precisar digitar senha" -ForegroundColor White
Write-Host "- Os comandos gcloud funcionarao automaticamente" -ForegroundColor White
Write-Host "- A autenticacao vai persistir entre sessoes" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "- Se mudar de computador, precisa configurar novamente" -ForegroundColor White
Write-Host "- Se as credenciais expirarem (apos varios meses), execute este script novamente" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"

