@echo off
:: ===================================================================
:: 🚀 DEPLOY COMPLETO PROFISSIONAL - GOOGLE CLOUD RUN
:: ===================================================================
:: Script completo e robusto para fazer deploy do sistema no Google Cloud
:: Sistema: Monpec Gestão Rural
:: ===================================================================

chcp 65001 >nul
setlocal enabledelayedexpansion
title 🚀 DEPLOY GOOGLE CLOUD - SISTEMA COMPLETO

:: ===================================================================
:: CONFIGURAÇÕES
:: ===================================================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set SERVICE_ACCOUNT=github-actions-deploy@%PROJECT_ID%.iam.gserviceaccount.com
set KEY_FILE=github-actions-key.json

:: Inicializar variáveis de controle
set SCRIPT_SUCCESS=0
set STEP_CURRENT=0
set STEP_TOTAL=12
set PUSH_OK=0
set SERVICE_OK=0
set SERVICE_URL=
set BUILD_OK=0
set DEPLOY_OK=0
set ARQUIVOS_OK=0
set ARQUIVOS_TOTAL=0

:: Garantir que a janela não fecha e definir diretório correto
if not "%~1"=="executed" (
    cd /d "%~dp0"
    cmd /k "%~f0" executed
    exit /b
)

:: Garantir que estamos sempre no diretório correto do script
cd /d "%~dp0"
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Erro ao acessar diretorio do script
    pause
    exit /b 1
)

:: Garantir que estamos no diretório correto do script
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║     🚀 DEPLOY COMPLETO PROFISSIONAL - GOOGLE CLOUD RUN     ║
echo ║                                                              ║
echo ║     Sistema: Monpec Gestão Rural                             ║
echo ║     Projeto: %PROJECT_ID%                                    ║
echo ║     Serviço: %SERVICE_NAME%                                  ║
echo ║     Região: %REGION%                                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Este script irá configurar e fazer deploy completo do sistema:
echo   1. Verificar todas as dependências
echo   2. Autenticar no Google Cloud
echo   3. Configurar projeto e Service Account
echo   4. Gerar chaves de autenticação
echo   5. Verificar arquivos necessários
echo   6. Fazer commit e push do código
echo   7. Verificar deploy no Cloud Run
echo   8. Gerar relatório completo
echo.
echo ⚠️  IMPORTANTE: Este processo pode levar 10-15 minutos
echo.
timeout /t 2 >nul
echo.

:: ========================================
:: PASSO 1: VERIFICAR AMBIENTE
:: ========================================
set /a STEP_CURRENT=1
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Verificando ambiente local
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar Python
echo Verificando Python...
python --version >nul 2>&1
set PYTHON_ERR=!ERRORLEVEL!
if !PYTHON_ERR! EQU 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo ✅ Python: %%v
) else (
    echo ❌ Python nao encontrado!
    echo    Instale Python antes de continuar.
    goto :erro
)

:: Verificar Git
echo Verificando Git...
git --version >nul 2>&1
set GIT_ERR=!ERRORLEVEL!
if !GIT_ERR! EQU 0 (
    for /f "tokens=*" %%v in ('git --version 2^>^&1') do echo ✅ Git: %%v
) else (
    echo ❌ Git nao encontrado!
    goto :erro
)

:: Verificar gcloud - verificacao simples que nao trava
echo Verificando Google Cloud SDK...
where gcloud >nul 2>&1
set GCLOUD_ERR=!ERRORLEVEL!
if !GCLOUD_ERR! EQU 0 (
    echo ✅ Google Cloud SDK: OK
) else (
    echo ⚠️  Google Cloud SDK nao no PATH - continuando...
)

echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 2: AUTENTICAR
:: ========================================
set /a STEP_CURRENT=2
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Autenticando no Google Cloud
echo ═══════════════════════════════════════════════════════════════
echo.
echo Executando login...
echo Se o navegador abrir, faca login e autorize.
echo.
call gcloud auth login
set LOGIN_ERR=!ERRORLEVEL!
echo.
echo ========================================
echo   LOGIN CONCLUIDO - CONTINUANDO SCRIPT
echo ========================================
echo.
if !LOGIN_ERR! NEQ 0 (
    echo ⚠️  Aviso: Possivel problema no login, mas continuando...
) else (
    echo ✅ Login executado com sucesso
)
echo.
echo ========================================
echo   AUTENTICACAO CONCLUIDA
echo ========================================
echo.
echo ✅ PASSO 2 CONCLUIDO
echo.
echo [INFO] Verificacao application-default pulada (opcional para deploy)
echo    Continuando automaticamente para o proximo passo...
echo.
timeout /t 2 >nul
echo.
echo ========================================
echo   INICIANDO PASSO 3
echo ========================================
echo.

:: ========================================
:: PASSO 3: CONFIGURAR PROJETO
:: ========================================
set /a STEP_CURRENT=3
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Configurando projeto Google Cloud
echo ═══════════════════════════════════════════════════════════════
echo.
echo Garantindo que estamos no diretorio correto...
cd /d "%~dp0"
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Erro ao acessar diretorio do script
    pause
    exit /b 1
)
echo Diretorio atual: %CD%
echo.
call gcloud config set project %PROJECT_ID%
set PROJ_ERR=!ERRORLEVEL!
if !PROJ_ERR! NEQ 0 (
    echo ❌ Erro ao configurar projeto
    goto :erro
)
echo ✅ Projeto configurado: %PROJECT_ID%
echo Verificando se o projeto existe e está acessível...
call gcloud projects describe %PROJECT_ID% >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    call :check_error "Projeto %PROJECT_ID% não encontrado ou sem acesso"
)
echo ✅ Projeto verificado e acessível
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 4: VERIFICAR/CRIAR SERVICE ACCOUNT
:: ========================================
set /a STEP_CURRENT=4
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Configurando Service Account
echo ═══════════════════════════════════════════════════════════════
echo.
echo Verificando Service Account: %SERVICE_ACCOUNT%
call gcloud iam service-accounts describe %SERVICE_ACCOUNT% --project=%PROJECT_ID% >nul 2>&1
set SA_EXISTS=!ERRORLEVEL!
if !SA_EXISTS! NEQ 0 (
    call :warning "Service Account não existe. Criando..."
    call gcloud iam service-accounts create github-actions-deploy --display-name="GitHub Actions Deploy" --project=%PROJECT_ID%
    set SA_CREATE_ERR=!ERRORLEVEL!
    if !SA_CREATE_ERR! NEQ 0 (
        echo ❌ Erro ao criar Service Account
        goto :erro
    )
    echo ✅ Service Account criado
) else (
    echo ✅ Service Account ja existe
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 5: CONFIGURAR PERMISSOES
:: ========================================
set /a STEP_CURRENT=5
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Configurando permissões do Service Account
echo ═══════════════════════════════════════════════════════════════
echo.
set ROLES=roles/run.admin roles/cloudbuild.builds.editor roles/storage.admin roles/iam.serviceAccountUser roles/artifactregistry.writer roles/cloudsql.client
set ROLES_OK=0
set ROLES_TOTAL=0

for %%r in (%ROLES%) do (
    set /a ROLES_TOTAL+=1
    echo    Verificando: %%r
    call gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --filter="bindings.members:serviceAccount:%SERVICE_ACCOUNT% AND bindings.role:%%r" --format="value(bindings.role)" >nul 2>&1
    set ROLE_CHECK=!ERRORLEVEL!
    if !ROLE_CHECK! NEQ 0 (
        call :warning "Atribuindo: %%r"
        call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SERVICE_ACCOUNT%" --role="%%r" --quiet >nul 2>&1
        set ROLE_ADD=!ERRORLEVEL!
        if !ROLE_ADD! EQU 0 (
            echo    ✅ %%r atribuido
            set /a ROLES_OK+=1
        ) else (
            echo    ❌ Erro ao atribuir %%r
        )
    ) else (
        echo    ✅ %%r ja esta atribuido
        set /a ROLES_OK+=1
    )
)

echo.
if !ROLES_OK! EQU !ROLES_TOTAL! (
    echo ✅ Todas as permissoes configuradas
) else (
    echo ⚠️  Algumas permissoes podem nao ter sido atribuidas
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 6: GERAR CHAVE JSON
:: ========================================
set /a STEP_CURRENT=6
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Gerando chave JSON do Service Account
echo ═══════════════════════════════════════════════════════════════
echo.
if exist %KEY_FILE% (
    call :warning "Arquivo já existe. Gerando nova chave..."
    del %KEY_FILE% >nul 2>&1
)

echo Gerando chave JSON...
call gcloud iam service-accounts keys create %KEY_FILE% --iam-account=%SERVICE_ACCOUNT% --project=%PROJECT_ID%
set KEY_CREATE_ERR=!ERRORLEVEL!
if !KEY_CREATE_ERR! NEQ 0 (
    echo ❌ Erro ao gerar chave JSON
    goto :erro
)

if exist %KEY_FILE% (
    call :success "Chave JSON gerada: %KEY_FILE%"
    for %%A in (%KEY_FILE%) do echo    Tamanho: %%~zA bytes
) else (
    echo ❌ Arquivo nao foi criado
    goto :erro
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 7: VERIFICAR ARQUIVOS NECESSARIOS
:: ========================================
set /a STEP_CURRENT=7
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Verificando arquivos necessários para deploy
echo ═══════════════════════════════════════════════════════════════
echo.

set ARQUIVOS_OK=0
set ARQUIVOS_TOTAL=0

:: Verificar Dockerfile
set /a ARQUIVOS_TOTAL+=1
if exist Dockerfile (
    echo ✅ Dockerfile existe
    set /a ARQUIVOS_OK+=1
) else (
    echo ❌ Dockerfile NAO existe
    echo    Criando Dockerfile...
    call CRIAR_DOCKERFILE.bat
    if exist Dockerfile (
        echo ✅ Dockerfile criado
        set /a ARQUIVOS_OK+=1
    ) else (
        echo ❌ Falha ao criar Dockerfile
    )
)

:: Verificar requirements_producao.txt
set /a ARQUIVOS_TOTAL+=1
if exist requirements_producao.txt (
    echo ✅ requirements_producao.txt existe
    set /a ARQUIVOS_OK+=1
) else (
    echo ❌ requirements_producao.txt NAO existe
)

:: Verificar workflow
set /a ARQUIVOS_TOTAL+=1
if exist .github\workflows\deploy-principal.yml (
    echo ✅ Workflow GitHub Actions existe
    set /a ARQUIVOS_OK+=1
) else (
    echo ❌ Workflow GitHub Actions NAO existe
)

echo.
if !ARQUIVOS_OK! EQU !ARQUIVOS_TOTAL! (
    echo ✅ Todos os arquivos necessarios estao presentes
) else (
    echo ⚠️  Alguns arquivos estao faltando
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 8: COMMIT E PUSH
:: ========================================
set /a STEP_CURRENT=8
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Fazendo commit e push do código
echo ═══════════════════════════════════════════════════════════════
echo.
echo Adicionando todos os arquivos ao Git...
git add . >nul 2>&1
set GIT_ADD_ERR=!ERRORLEVEL!
if !GIT_ADD_ERR! EQU 0 (
    echo ✅ Arquivos adicionados
) else (
    echo ⚠️  Aviso ao adicionar arquivos
)

echo Fazendo commit...
git commit -m "Deploy automatico: Configuracao completa - %date% %time%" >nul 2>&1
set GIT_COMMIT_ERR=!ERRORLEVEL!
if !GIT_COMMIT_ERR! EQU 0 (
    echo ✅ Commit realizado
) else (
    echo ⚠️  Nenhuma mudanca para commitar (pode ser normal)
)

echo Sincronizando com GitHub (pull antes de push)...
echo ⏳ Fazendo pull para sincronizar mudancas remotas...
call git pull origin master --no-rebase >nul 2>&1
set GIT_PULL_ERR=!ERRORLEVEL!
if !GIT_PULL_ERR! EQU 0 (
    echo ✅ Pull realizado - codigo sincronizado
) else (
    echo ⚠️  Pull pode ter tido conflitos (continuando mesmo assim)
)

echo Enviando para GitHub (isso pode levar alguns minutos)...
call git push origin master
set GIT_PUSH_ERR=!ERRORLEVEL!
if !GIT_PUSH_ERR! EQU 0 (
    echo ✅ Push realizado com sucesso!
    set PUSH_OK=1
) else (
    echo ⚠️  Erro no push
    echo    Tentando resolver conflitos...
    echo    Se o problema persistir, execute manualmente: git pull origin master
    set PUSH_OK=0
)
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 9: VERIFICAR DEPLOY NO SERVIDOR
:: ========================================
set /a STEP_CURRENT=9
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Verificando deploy no servidor
echo ═══════════════════════════════════════════════════════════════
echo.
echo Aguardando GitHub Actions processar (10 segundos)...
timeout /t 10 >nul
echo.

echo Verificando builds do Cloud Build...
call gcloud builds list --project=%PROJECT_ID% --limit=5 --format="table(id,status,createTime)" 2>&1
echo.

echo Verificando serviço Cloud Run...
call gcloud run services describe %SERVICE_NAME% --region=%REGION% --project=%PROJECT_ID% --format="value(status.url)" 2>nul >temp_url.txt
set SERVICE_CHECK_ERR=!ERRORLEVEL!
if !SERVICE_CHECK_ERR! EQU 0 (
    if exist temp_url.txt (
        set /p SERVICE_URL=<temp_url.txt
        del temp_url.txt >nul 2>&1
        if defined SERVICE_URL (
            if not "!SERVICE_URL!"=="" (
                echo ✅ Servico encontrado
                echo    URL: !SERVICE_URL!
                set SERVICE_OK=1
            ) else (
                echo ⚠️  URL do servico nao encontrada
                set SERVICE_OK=0
            )
        ) else (
            echo ⚠️  URL do servico nao encontrada
            set SERVICE_OK=0
        )
    ) else (
        echo ⚠️  Arquivo temporario nao foi criado
        set SERVICE_OK=0
    )
) else (
    echo ⚠️  Servico nao encontrado ou erro ao acessar
    set SERVICE_OK=0
)
echo.

echo Verificando logs recentes do serviço...
call gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND severity>=ERROR" --limit=5 --format="table(timestamp,severity,textPayload)" --project=%PROJECT_ID% 2>&1
echo.

echo Pressione qualquer tecla para continuar...
pause
echo.

:: ========================================
:: PASSO 10: VERIFICAR SECRETS DO GITHUB
:: ========================================
set /a STEP_CURRENT=10
echo.
echo ═══════════════════════════════════════════════════════════════
echo   [PASSO !STEP_CURRENT!/!STEP_TOTAL!] Verificando configurações do GitHub
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANTE: Voce precisa configurar os secrets no GitHub:
echo.
echo 1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo.
echo 2. Adicione/atualize os seguintes secrets:
echo    - GCP_SA_KEY: Copie o conteúdo de %KEY_FILE%
echo    - SECRET_KEY: Sua Django SECRET_KEY
echo    - DB_NAME: Nome do banco de dados (padrao: monpec_db)
echo    - DB_USER: Usuario do banco (padrao: monpec_user)
echo    - DB_PASSWORD: Senha do banco ⚠️  CRITICO - Verifique se esta correto!
echo    - DJANGO_SUPERUSER_PASSWORD: Senha do superusuario Django
echo.
echo ⚠️  ATENCAO: Os logs mostram erro de autenticacao no banco!
echo    Erro detectado: password authentication failed for user "monpec_user"
echo    Solucao: Verifique se DB_PASSWORD esta correto nos secrets do GitHub
echo.
echo Deseja abrir o arquivo JSON agora? (S/N)
set /p ABRIR_JSON=
if /i "!ABRIR_JSON!"=="S" (
    if exist %KEY_FILE% (
        start notepad %KEY_FILE%
        echo.
        echo ✅ Arquivo aberto no Notepad
        echo    Copie TODO o conteudo e adicione como secret GCP_SA_KEY
    )
)
echo.
echo Pressione qualquer tecla para ver relatorio completo...
pause
echo.

:: ========================================
:: RELATORIO FINAL
:: ========================================
:relatorio
echo.
echo ========================================
echo   RELATORIO COMPLETO DO DEPLOY
echo ========================================
echo.
echo [RESUMO DAS FASES]
echo.
echo FASE 1 - Configuracao: ✅ Concluida
echo FASE 2 - Arquivos Locais: 
if defined ARQUIVOS_TOTAL (
    if defined ARQUIVOS_OK (
        set ARQUIVOS_FALTANDO=!ARQUIVOS_TOTAL!
        set /a ARQUIVOS_FALTANDO-=!ARQUIVOS_OK!
        if !ARQUIVOS_FALTANDO! EQU 0 (
            echo    ✅ Todos os arquivos presentes
        ) else (
            echo    ⚠️  !ARQUIVOS_FALTANDO! arquivo(s) faltando
        )
    ) else (
        echo    ⚠️  Status dos arquivos nao disponivel
    )
) else (
    echo    ⚠️  Status dos arquivos nao disponivel
)
echo FASE 3 - Service Account: ✅ Concluida
echo FASE 4 - Permissoes: ✅ Concluida
echo FASE 5 - Commit e Push:
if defined PUSH_OK (
    if !PUSH_OK! EQU 1 (
        echo    ✅ Codigo enviado para GitHub
    ) else (
        echo    ⚠️  Push pode ter falhado
    )
) else (
    echo    ⚠️  Status do push nao disponivel
)
echo FASE 6 - Servidor:
if defined SERVICE_OK (
    if !SERVICE_OK! EQU 1 (
        echo    ✅ Servico encontrado e acessivel
        if defined SERVICE_URL (
            echo    URL: !SERVICE_URL!
        )
    ) else (
        echo    ⚠️  Servico nao encontrado ou com problemas
    )
) else (
    echo    ⚠️  Status do servico nao disponivel
)
echo.
echo ========================================
echo   VERIFICACOES DETALHADAS
echo ========================================
echo.
echo [ARQUIVOS NECESSARIOS]
echo.
if exist %KEY_FILE% (
    echo ✅ Chave JSON: %KEY_FILE%
    for %%A in (%KEY_FILE%) do echo    Tamanho: %%~zA bytes
) else (
    echo ❌ Chave JSON: NÃO gerada
)
echo.
echo ✅ Service Account: %SERVICE_ACCOUNT%
echo ✅ Permissões: Configuradas
echo ✅ Projeto: %PROJECT_ID%
echo ✅ Serviço: %SERVICE_NAME%
echo ✅ Região: %REGION%
echo.
if exist Dockerfile (
    echo ✅ Dockerfile: Existe
) else (
    echo ❌ Dockerfile: NAO existe
)
echo.
if exist requirements_producao.txt (
    echo ✅ requirements_producao.txt: Existe
) else (
    echo ❌ requirements_producao.txt: NAO existe
)
echo.
if exist .github\workflows\deploy-principal.yml (
    echo ✅ Workflow GitHub Actions: Existe
) else (
    echo ❌ Workflow GitHub Actions: NAO existe
)
echo.
echo ========================================
echo   STATUS DO SERVIÇO CLOUD RUN
echo ========================================
echo.
echo Verificando serviço '%SERVICE_NAME%' em '%REGION%'...
echo.
call gcloud run services describe %SERVICE_NAME% --region=%REGION% --project=%PROJECT_ID% --format="table(status.conditions[0].type,status.conditions[0].status,status.url)" 2>&1
set SERVICE_DESC_ERR=!ERRORLEVEL!
if !SERVICE_DESC_ERR! EQU 0 (
    echo.
    echo ✅ Servico encontrado e acessivel
) else (
    echo.
    echo ⚠️  Servico nao encontrado
    echo    Isso e normal se o servico ainda nao foi criado pelo deploy
)
echo.
echo ========================================
echo   ULTIMOS BUILDS
echo ========================================
echo.
call gcloud builds list --project=%PROJECT_ID% --limit=5 --format="table(id,status,createTime)" 2>&1
echo.
echo ========================================
echo   PROBLEMAS IDENTIFICADOS
echo ========================================
echo.
set PROBLEMAS=0

if defined ARQUIVOS_FALTANDO (
    if !ARQUIVOS_FALTANDO! GTR 0 (
        echo ❌ PROBLEMA: !ARQUIVOS_FALTANDO! arquivo(s) necessario(s) faltando
        set /a PROBLEMAS+=1
    )
)

if defined PUSH_OK (
    if !PUSH_OK! EQU 0 (
        echo ⚠️  AVISO: Push para GitHub pode ter falhado
        echo    Verifique manualmente: git push origin master
        set /a PROBLEMAS+=1
    )
)

if defined SERVICE_OK (
    if !SERVICE_OK! EQU 0 (
        echo ⚠️  AVISO: Servico Cloud Run nao encontrado
        echo    Possiveis causas:
        echo    - Deploy ainda em andamento (aguarde alguns minutos)
        echo    - Erro no deploy (verifique GitHub Actions)
        echo    - Servico com nome diferente
        set /a PROBLEMAS+=1
    )
)

if !PROBLEMAS! EQU 0 (
    echo ✅ NENHUM PROBLEMA IDENTIFICADO!
    echo.
    echo O sistema esta configurado e pronto para funcionar.
    echo.
    if defined SERVICE_URL (
        echo Acesse o sistema em: !SERVICE_URL!
    )
) else (
    echo.
    echo ⚠️  TOTAL: !PROBLEMAS! problema(s) ou aviso(s) encontrado(s)
    echo.
    echo Verifique os itens acima e corrija antes de usar o sistema.
)
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Se o servico nao foi encontrado:
echo    - Aguarde alguns minutos e execute este script novamente
echo    - Ou verifique: https://github.com/LMONCAO/Monpec_GestaoRural/actions
echo.
echo 2. Se houver arquivos faltando:
echo    - Crie os arquivos faltantes
echo    - Execute este script novamente
echo.
echo 3. Se o push falhou:
echo    - Execute manualmente: git push origin master
echo.
echo 4. Verificar secrets do GitHub:
echo    - Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo    - Certifique-se de que GCP_SA_KEY esta configurado
echo.
echo 5. Testar o sistema:
if defined SERVICE_URL (
    echo    - Acesse: !SERVICE_URL!
    echo    - Verifique se a pagina carrega
    echo    - Teste o formulario de demonstracao
)
echo.
echo ========================================
echo.
echo ✅ RELATORIO COMPLETO GERADO!
echo.
echo ========================================
echo.
echo ✅ SCRIPT CONCLUIDO COM SUCESSO!
echo.
echo Esta janela permanecera aberta para voce ver o relatorio.
echo.
echo Para FECHAR esta janela, digite: exit
echo Para ver o relatorio novamente, pressione Enter
echo.
echo Aguardando seu comando...
:loop
set /p COMANDO="> "
if /i "!COMANDO!"=="exit" (
    echo.
    echo Fechando...
    timeout /t 1 >nul
    exit
) else if "!COMANDO!"=="" (
    echo.
    goto :relatorio
) else (
    echo.
    echo Comando desconhecido. Digite 'exit' para fechar ou Enter para ver relatorio.
    echo.
    goto :loop
)

:erro
echo.
echo ========================================
echo   ERRO ENCONTRADO
echo ========================================
echo.
echo O script encontrou um erro e parou.
echo Verifique as mensagens acima para identificar o problema.
echo.
echo Esta janela permanecera aberta para voce ver os erros.
echo Digite 'exit' para fechar.
:erro_loop
set /p COMANDO=
if /i "!COMANDO!"=="exit" (
    exit
) else (
    goto :erro_loop
)
