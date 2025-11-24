# Script para Configurar Domínio monpec.com.br no Google Cloud Run
# Autor: Assistente AI
# Data: 2025

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurar Domínio monpec.com.br" -ForegroundColor Cyan
Write-Host "Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o gcloud CLI está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "⚠️  Google Cloud CLI não encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Instalar o Google Cloud CLI: https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    Write-Host "2. Use o Console Web: https://console.cloud.google.com/run" -ForegroundColor White
    Write-Host ""
    Write-Host "Pressione qualquer tecla para abrir o guia completo de configuração..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Start-Process "CONFIGURAR_DOMINIO.md"
    exit
}

# Verificar se está autenticado
Write-Host "Verificando autenticação no Google Cloud..." -ForegroundColor Yellow
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or -not $authStatus) {
    Write-Host "❌ Não autenticado no Google Cloud!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute: gcloud auth login" -ForegroundColor Yellow
    exit
}

Write-Host "✅ Autenticado como: $authStatus" -ForegroundColor Green
Write-Host ""

# Definir variáveis
$domain = "monpec.com.br"
$service = "monpec"
$region = "us-central1"

Write-Host "Configurações:" -ForegroundColor Cyan
Write-Host "  Domínio: $domain" -ForegroundColor White
Write-Host "  Serviço: $service" -ForegroundColor White
Write-Host "  Região: $region" -ForegroundColor White
Write-Host ""

# Verificar se o serviço existe
Write-Host "Verificando serviço Cloud Run..." -ForegroundColor Yellow
$serviceExists = gcloud run services describe $service --region $region --format="value(name)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Serviço '$service' não encontrado na região '$region'!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique o nome do serviço e região:" -ForegroundColor Yellow
    Write-Host "  gcloud run services list --region $region" -ForegroundColor White
    exit
}

Write-Host "✅ Serviço encontrado!" -ForegroundColor Green
Write-Host ""

# Menu principal
Write-Host "O que você deseja fazer?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Criar mapeamento de domínio (novo)" -ForegroundColor White
Write-Host "2. Ver mapeamento existente" -ForegroundColor White
Write-Host "3. Listar todos os domínios mapeados" -ForegroundColor White
Write-Host "4. Ver registros DNS necessários" -ForegroundColor White
Write-Host "5. Remover mapeamento de domínio" -ForegroundColor White
Write-Host "6. Ver logs do serviço" -ForegroundColor White
Write-Host "7. Abrir guia completo (CONFIGURAR_DOMINIO.md)" -ForegroundColor White
Write-Host "0. Sair" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Escolha uma opção (0-7)"

switch ($opcao) {
    "1" {
        Write-Host ""
        Write-Host "Criando mapeamento de domínio..." -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "⚠️  IMPORTANTE: Após criar o mapeamento, você receberá registros DNS." -ForegroundColor Yellow
        Write-Host "   Adicione esses registros no painel do seu provedor de domínio!" -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "Continuar? (S/N)"
        if ($confirm -ne "S" -and $confirm -ne "s") {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
            exit
        }
        
        Write-Host ""
        gcloud run domain-mappings create --service $service --domain $domain --region $region
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Mapeamento criado com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
            Write-Host "1. Anote os registros DNS que apareceram acima" -ForegroundColor White
            Write-Host "2. Acesse o painel do seu provedor de domínio" -ForegroundColor White
            Write-Host "3. Adicione os registros DNS fornecidos" -ForegroundColor White
            Write-Host "4. Aguarde a propagação DNS (15 minutos - 2 horas)" -ForegroundColor White
            Write-Host ""
            Write-Host "Para ver os registros DNS novamente:" -ForegroundColor Yellow
            Write-Host "  gcloud run domain-mappings describe $domain --region $region" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "❌ Erro ao criar mapeamento!" -ForegroundColor Red
            Write-Host "Verifique se o domínio já não está mapeado ou há problemas de permissão." -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Verificando mapeamento de domínio..." -ForegroundColor Yellow
        Write-Host ""
        gcloud run domain-mappings describe $domain --region $region --format="yaml"
    }
    
    "3" {
        Write-Host ""
        Write-Host "Listando todos os domínios mapeados..." -ForegroundColor Yellow
        Write-Host ""
        gcloud run domain-mappings list --region $region
    }
    
    "4" {
        Write-Host ""
        Write-Host "Verificando registros DNS necessários..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Registros DNS que você precisa adicionar no seu provedor:" -ForegroundColor Cyan
        Write-Host ""
        
        gcloud run domain-mappings describe $domain --region $region --format="value(metadata.name)" | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            $mapping = gcloud run domain-mappings describe $domain --region $region --format="json" | ConvertFrom-Json
            Write-Host "Domínio: $domain" -ForegroundColor White
            Write-Host "Status: $($mapping.status.conditions[0].status)" -ForegroundColor White
            Write-Host ""
            Write-Host "Registros DNS:" -ForegroundColor Cyan
            
            # Verificar se há registros DNS nas anotações
            $resourceRecords = gcloud run domain-mappings describe $domain --region $region --format="value(status.resourceRecords)" 2>&1
            if ($resourceRecords) {
                Write-Host $resourceRecords -ForegroundColor White
            } else {
                Write-Host "Execute o comando completo para ver os registros:" -ForegroundColor Yellow
                Write-Host "  gcloud run domain-mappings describe $domain --region $region" -ForegroundColor White
            }
        } else {
            Write-Host "❌ Domínio não encontrado!" -ForegroundColor Red
            Write-Host "Crie o mapeamento primeiro (opção 1)" -ForegroundColor Yellow
        }
    }
    
    "5" {
        Write-Host ""
        Write-Host "⚠️  ATENÇÃO: Isso removerá o mapeamento de domínio!" -ForegroundColor Red
        Write-Host ""
        $confirm = Read-Host "Tem certeza que deseja remover o mapeamento de $domain? (digite 'SIM' para confirmar)"
        if ($confirm -eq "SIM") {
            gcloud run domain-mappings delete $domain --region $region
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✅ Mapeamento removido com sucesso!" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "❌ Erro ao remover mapeamento!" -ForegroundColor Red
            }
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
        }
    }
    
    "6" {
        Write-Host ""
        Write-Host "Últimos logs do serviço..." -ForegroundColor Yellow
        Write-Host ""
        $limit = Read-Host "Quantas linhas de log deseja ver? (padrão: 50)"
        if (-not $limit) { $limit = 50 }
        gcloud run services logs read $service --region $region --limit $limit
    }
    
    "7" {
        Write-Host ""
        Write-Host "Abrindo guia completo..." -ForegroundColor Yellow
        Start-Process "CONFIGURAR_DOMINIO.md"
    }
    
    "0" {
        Write-Host ""
        Write-Host "Saindo..." -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Opção inválida!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Operação concluída!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


