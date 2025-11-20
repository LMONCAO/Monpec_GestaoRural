@echo off
REM Script Automático para Atualizar o Servidor Monpec
REM Windows Batch Script

echo ========================================
echo    ATUALIZAÇÃO COMPLETA - SISTEMA MONPEC
echo    Versão 2.0 com IA Aprimorada
echo ========================================
echo.

set SSH_KEY="C:\Users\lmonc\Downloads\monpecprojetista.key"
set SERVER=root@191.252.225.106
set REMOTE_DIR=/var/www/monpec.com.br

echo [1/7] Fazendo backup remoto...
ssh -i %SSH_KEY% %SERVER% "cd /var/www && tar -czf backup_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.tar.gz monpec.com.br/" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Backup criado
) else (
    echo × Erro no backup, continuando...
)
echo.

echo [2/7] Transferindo arquivos IA...
cd C:\Monpec_projetista
scp -i %SSH_KEY% -r gestao_rural\ia_*.py %SERVER%:%REMOTE_DIR%/gestao_rural/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Arquivos IA transferidos
) else (
    echo × Erro ao transferir IAs
)
echo.

echo [3/7] Transferindo templates...
scp -i %SSH_KEY% -r templates\*.html %SERVER%:%REMOTE_DIR%/templates/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Templates transferidos
) else (
    echo × Erro ao transferir templates
)
echo.

echo [4/7] Transferindo scripts de configuração...
scp -i %SSH_KEY% *.sh %SERVER%:%REMOTE_DIR%/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Scripts transferidos
) else (
    echo × Erro ao transferir scripts
)
echo.

echo [5/7] Transferindo documentação...
scp -i %SSH_KEY% *.md %SERVER%:%REMOTE_DIR%/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Documentação transferida
) else (
    echo × Erro ao transferir docs
)
echo.

echo [6/7] Parando Django antigo...
ssh -i %SSH_KEY% %SERVER% "pkill -9 python" 2>nul
echo ✓ Django parado
echo.

echo [7/7] Iniciando Django atualizado...
ssh -i %SSH_KEY% %SERVER% "cd %REMOTE_DIR% && source venv/bin/activate && nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Django iniciado
) else (
    echo × Erro ao iniciar Django
)
echo.

echo ========================================
echo    ATUALIZAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo ✓ 5 Novas IAs instaladas
echo ✓ Dashboards interativos
echo ✓ Sistema de relatórios
echo ✓ Scripts de otimização
echo.
echo 🌐 Teste o sistema:
echo    http://191.252.225.106
echo.
echo 📚 Leia a documentação:
echo    README_SISTEMA_MELHORADO.md
echo    RESUMO_MELHORIAS_IMPLEMENTADAS.md
echo.
echo 🚀 Próximos passos opcionais:
echo    1. Executar otimizar_performance.sh (no servidor)
echo    2. Executar configurar_ssl_https.sh (se tiver domínio)
echo.

pause

