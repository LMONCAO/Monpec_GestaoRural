@echo off
chcp 65001 >nul
echo ========================================
echo   TESTAR SISTEMA COMPLETO
echo ========================================
echo.

set URL=https://monpec-fzzfjppzva-uc.a.run.app

echo ???? Testando URL: %URL%
echo.

echo 1. Testando resposta HTTP...
powershell -Command "try {  = Invoke-WebRequest -Uri '%URL%' -Method Get -TimeoutSec 10; Write-Host '??? Status:' .StatusCode -ForegroundColor Green } catch { Write-Host '??? Erro:' .Exception.Message -ForegroundColor Red }"

echo.
echo 2. Testando imagens do slide...
for /L %%i in (1,1,6) do (
    echo    Testando foto%%i.jpeg...
    powershell -Command "try {  = Invoke-WebRequest -Uri '%URL%/static/site/foto%%i.jpeg' -Method Head -TimeoutSec 5; Write-Host '   ??? foto%%i.jpeg: OK' -ForegroundColor Green } catch { Write-Host '   ??? foto%%i.jpeg: FALHOU' -ForegroundColor Red }"
)

echo.
echo 3. Verificando logs recentes...
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=3 --format="value(textPayload)" --project=monpec-sistema-rural 2>nul | findstr /C:"certificado_digital" >nul
if errorlevel 1 (
    echo    ??? Nenhum erro de certificado_digital encontrado recentemente
) else (
    echo    ??????  Ainda h?? erros de certificado_digital - migrations podem n??o ter sido aplicadas
)

echo.
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo ??? Servi??o: https://monpec-fzzfjppzva-uc.a.run.app
echo.
echo ???? Pr??ximos passos:
echo    1. Acesse a URL acima no navegador
echo    2. Verifique se as imagens do slide aparecem
echo    3. Teste o formul??rio de demonstra????o
echo    4. Se ainda houver erro de certificado_digital, execute:
echo       .\APLICAR_MIGRATIONS_SIMPLES.bat
echo.

pause