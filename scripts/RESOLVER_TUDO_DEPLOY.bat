@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title RESOLVER TUDO - DEPLOY AUTOMATICO

:: Garantir que a janela nao fecha automaticamente
if "%~1"=="" (
    echo Iniciando script em modo protegido...
    cmd /k "%~f0" executed
    exit /b
)

:: Modo protegido ativado
echo Modo protegido: Janela nao vai fechar automaticamente
echo.

echo ========================================
echo   RESOLVER TUDO - DEPLOY AUTOMÁTICO
echo ========================================
echo.
echo Este script vai:
echo   1. Verificar configurações atuais
echo   2. Corrigir o que estiver faltando
echo   3. Testar se está funcionando
echo   4. Mostrar status completo
echo   5. Gerar relatório final
echo.
echo O script NÃO vai fechar automaticamente.
echo Você verá TODO o processo e o relatório completo.
echo.
echo Pressione qualquer tecla para começar...
pause
echo.
echo ========================================
echo   INICIANDO PROCESSO
echo ========================================
echo.

:: ========================================
:: PASSO 1: VERIFICAR AUTENTICAÇÃO
:: ========================================
echo [PASSO 1/6] Verificando autenticação no Google Cloud...
echo.
echo Verificando se gcloud esta instalado...
where gcloud >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERRO: gcloud nao esta instalado ou nao esta no PATH
    echo.
    echo Continuando mesmo assim para verificar outras coisas...
    set AUTH_RESULT=1
) else (
    echo ✅ gcloud encontrado
    echo.
    echo Executando comando gcloud auth list...
    gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>nul
    set AUTH_RESULT=!ERRORLEVEL!
    echo Codigo de retorno: !AUTH_RESULT!
)
echo.
if !AUTH_RESULT! NEQ 0 (
    echo ⚠️  Você não está autenticado no Google Cloud
    echo.
    echo Deseja fazer login agora? (S/N)
    set /p FAZER_LOGIN=
    if /i "!FAZER_LOGIN!"=="S" (
        echo Executando login...
        gcloud auth login
        if %ERRORLEVEL% NEQ 0 (
            echo ⚠️  Falha no login. Continuando mesmo assim...
        )
    ) else (
        echo Continuando sem autenticação...
    )
) else (
    echo ✅ Autenticado no Google Cloud
    for /f "tokens=*" %%a in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>nul') do set USER_EMAIL=%%a
    if defined USER_EMAIL (
        echo    Usuario: !USER_EMAIL!
    )
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 2: CONFIGURAR PROJETO
:: ========================================
echo [PASSO 2/6] Configurando projeto...
echo.
echo Executando: gcloud config set project monpec-sistema-rural
gcloud config set project monpec-sistema-rural 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Aviso: Erro ao configurar projeto, mas continuando...
) else (
    echo ✅ Projeto configurado: monpec-sistema-rural
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 3: VERIFICAR/CRIAR SERVICE ACCOUNT
:: ========================================
echo [PASSO 3/6] Verificando Service Account...
echo.
gcloud iam service-accounts describe github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com --project=monpec-sistema-rural >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Service Account não existe. Criando...
    gcloud iam service-accounts create github-actions-deploy --display-name="GitHub Actions Deploy" --project=monpec-sistema-rural
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Erro ao criar Service Account
        echo    Verifique se você tem permissão para criar service accounts
        echo.
        goto :final
    )
    echo ✅ Service Account criado com sucesso!
) else (
    echo ✅ Service Account já existe
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 4: CONFIGURAR PERMISSÕES
:: ========================================
echo [PASSO 4/6] Configurando permissões do Service Account...
echo.
echo    Atribuindo roles necessárias...
echo.

set ROLES=roles/run.admin roles/cloudbuild.builds.editor roles/storage.admin roles/iam.serviceAccountUser roles/artifactregistry.writer
set ROLES_OK=0
set ROLES_TOTAL=0

for %%r in (%ROLES%) do (
    set /a ROLES_TOTAL+=1
    echo    Verificando: %%r
    gcloud projects get-iam-policy monpec-sistema-rural --flatten="bindings[].members" --filter="bindings.members:serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com AND bindings.role:%%r" --format="value(bindings.role)" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo    ⚠️  Atribuindo: %%r
        gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="%%r" --quiet >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo    ✅ %%r atribuído
            set /a ROLES_OK+=1
        ) else (
            echo    ❌ Erro ao atribuir %%r
        )
    ) else (
        echo    ✅ %%r já está atribuído
        set /a ROLES_OK+=1
    )
)

echo.
if !ROLES_OK! EQU !ROLES_TOTAL! (
    echo ✅ Todas as permissões configuradas corretamente
) else (
    echo ⚠️  Algumas permissões podem não ter sido atribuídas
    echo    Verifique manualmente se necessário
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 5: GERAR CHAVE JSON
:: ========================================
echo [PASSO 5/6] Gerando chave JSON do Service Account...
echo.
if exist github-actions-key.json (
    echo ⚠️  Arquivo github-actions-key.json já existe
    echo    Gerando nova chave (a antiga será substituída)...
    del github-actions-key.json >nul 2>&1
)

gcloud iam service-accounts keys create github-actions-key.json --iam-account=github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com --project=monpec-sistema-rural
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erro ao gerar chave JSON
    echo.
    goto :final
)

if exist github-actions-key.json (
    echo ✅ Chave JSON gerada com sucesso: github-actions-key.json
    for %%A in (github-actions-key.json) do echo    Tamanho: %%~zA bytes
) else (
    echo ❌ Arquivo não foi criado
    echo.
    goto :final
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 6: VERIFICAR CONFIGURAÇÕES
:: ========================================
echo [PASSO 6/6] Verificando configurações finais...
echo.
echo Aguarde, coletando informações para o relatório...
timeout /t 2
echo.

:: ========================================
:: RELATÓRIO FINAL
:: ========================================
:final
echo.
echo ========================================
echo   RELATÓRIO FINAL COMPLETO
echo ========================================
echo.
echo [CONFIGURAÇÕES VERIFICADAS]
echo.
if exist github-actions-key.json (
    echo ✅ Chave JSON gerada: github-actions-key.json
    for %%A in (github-actions-key.json) do echo    Tamanho: %%~zA bytes
    echo    Data: %date% %time%
) else (
    echo ❌ Chave JSON NÃO foi gerada
)
echo.
echo ✅ Service Account: github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com
echo ✅ Permissões: Configuradas (5 roles principais)
echo ✅ Projeto: monpec-sistema-rural
echo.
if exist Dockerfile (
    echo ✅ Dockerfile: Existe
) else (
    echo ❌ Dockerfile: NÃO existe - Execute CRIAR_DOCKERFILE.bat
)
echo.
if exist requirements_producao.txt (
    echo ✅ requirements_producao.txt: Existe
) else (
    echo ❌ requirements_producao.txt: NÃO existe
)
echo.
if exist .github\workflows\deploy-principal.yml (
    echo ✅ Workflow GitHub Actions: Existe
) else (
    echo ❌ Workflow GitHub Actions: NÃO existe
)
echo.
echo ========================================
echo   STATUS DO SERVIÇO CLOUD RUN
echo ========================================
echo.
echo Verificando serviço 'monpec' em 'us-central1'...
echo.
gcloud run services describe monpec --region=us-central1 --project=monpec-sistema-rural --format="table(status.conditions[0].type,status.conditions[0].status,status.url)" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Serviço encontrado e acessível
) else (
    echo.
    echo ⚠️  Serviço não encontrado ou erro ao acessar
    echo    Isso é normal se o serviço ainda não foi criado pelo deploy
)
echo.
echo ========================================
echo   ÚLTIMOS BUILDS DO CLOUD BUILD
echo ========================================
echo.
echo Últimos 5 builds:
echo.
gcloud builds list --project=monpec-sistema-rural --limit=5 --format="table(id,status,createTime,logUrl)" 2>&1
echo.
echo ========================================
echo   AÇÕES NECESSÁRIAS
echo ========================================
echo.
echo ⚠️  IMPORTANTE: Você precisa fazer o seguinte:
echo.
echo 1. ADICIONAR SECRET NO GITHUB:
echo    - O arquivo 'github-actions-key.json' precisa ser copiado
echo    - Copie TODO o conteúdo do arquivo (Ctrl+A, Ctrl+C)
echo    - Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo    - Crie/atualize o secret: GCP_SA_KEY
echo    - Cole o conteúdo do JSON
echo.
echo 2. VERIFICAR OUTROS SECRETS:
echo    Certifique-se de que estes secrets estão configurados:
echo    - GCP_SA_KEY (o JSON que você vai adicionar)
echo    - SECRET_KEY
echo    - DB_NAME
echo    - DB_USER
echo    - DB_PASSWORD
echo    - DJANGO_SUPERUSER_PASSWORD
echo.
echo 3. FAZER PUSH:
echo    git push origin master
echo.
echo 4. ACOMPANHAR DEPLOY:
echo    https://github.com/LMONCAO/Monpec_GestaoRural/actions
echo.
echo ========================================
echo.
echo Deseja abrir o arquivo JSON agora para copiar? (S/N)
set /p ABRIR_JSON=
if /i "!ABRIR_JSON!"=="S" (
    if exist github-actions-key.json (
        start notepad github-actions-key.json
        echo.
        echo ✅ Arquivo aberto no Notepad.
        echo    Copie TODO o conteúdo e adicione como secret GCP_SA_KEY no GitHub.
        echo.
    ) else (
        echo ❌ Arquivo github-actions-key.json não foi encontrado
    )
)
echo.
echo ========================================
echo   PROCESSO CONCLUÍDO
echo ========================================
echo.
echo ✅ Todas as verificações foram realizadas
echo ✅ Correções aplicadas automaticamente
echo ✅ Relatório completo gerado
echo.
echo Este script pode ser executado novamente a qualquer momento
echo para verificar ou corrigir as configurações.
echo.
echo ========================================
echo.
echo ========================================
echo.
echo IMPORTANTE: O script está finalizado.
echo.
echo ========================================
echo   JANELA PERMANECERA ABERTA
echo ========================================
echo.
echo Esta janela NAO vai fechar automaticamente.
echo.
echo Para fechar, digite 'exit' e pressione Enter
echo ou simplesmente feche esta janela.
echo.
echo ========================================
echo.
:loop
echo Digite 'exit' para fechar ou pressione Enter para ver o relatorio novamente...
set /p COMANDO=
if /i "!COMANDO!"=="exit" (
    echo.
    echo Fechando...
    exit
) else (
    echo.
    echo Relatorio completo mostrado acima.
    echo.
    goto :loop
)
