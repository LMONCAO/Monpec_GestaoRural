@echo off
echo 🌐 CONECTANDO NA VM LOCAWEB
echo ============================

echo.
echo 📋 VERIFICAÇÕES NECESSÁRIAS:
echo 1. VM deve estar "Executando" no painel
echo 2. Verificar IP público da VM
echo 3. Verificar se SSH está habilitado
echo.

echo 🔍 TESTANDO CONEXÕES POSSÍVEIS:
echo.

echo Testando IP 10.1.1.234...
ping -n 1 10.1.1.234
if %errorlevel% equ 0 (
    echo ✅ IP 10.1.1.234 responde!
    echo Tentando SSH...
    ssh usuario@10.1.1.234
) else (
    echo ❌ IP 10.1.1.234 não responde
)

echo.
echo 🔧 ALTERNATIVAS:
echo 1. Verificar IP público no painel da Locaweb
echo 2. Usar console web da Locaweb
echo 3. Configurar SSH via painel
echo.

echo 📞 PRÓXIMOS PASSOS:
echo 1. Acesse o painel da Locaweb
echo 2. Vá em "VMs" → Sua VM
echo 3. Verifique o IP público
echo 4. Configure SSH se necessário
echo.

pause

