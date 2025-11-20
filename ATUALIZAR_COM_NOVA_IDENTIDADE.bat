@echo off
REM ========================================
REM  ATUALIZAÇÃO COMPLETA - NOVA IDENTIDADE
REM  Sistema Monpec 2.0
REM  Azul Marinho + Cinza Claro + Marrom Terra
REM ========================================

echo.
echo ========================================
echo    SISTEMA MONPEC 2.0
echo    Nova Identidade Visual
echo ========================================
echo.

set SSH_KEY="C:\Users\lmonc\Downloads\monpecprojetista.key"
set SERVER=root@191.252.225.106
set REMOTE=/var/www/monpec.com.br

echo [1/10] Criando diretorios no servidor...
ssh -i %SSH_KEY% %SERVER% "mkdir -p %REMOTE%/static/css %REMOTE%/gestao_rural/management/commands %REMOTE%/gestao_rural/fixtures %REMOTE%/gestao_rural/templatetags" 2>nul
echo OK
echo.

echo [2/10] Transferindo CSS (Identidade Visual)...
scp -i %SSH_KEY% static\css\identidade_visual.css %SERVER%:%REMOTE%/static/css/ 2>nul
echo OK
echo.

echo [3/10] Transferindo Template Tags (Formatacao BR)...
scp -i %SSH_KEY% gestao_rural\templatetags\formatacao_br.py %SERVER%:%REMOTE%/gestao_rural/templatetags/ 2>nul
echo OK
echo.

echo [4/10] Transferindo Modulos Python...
scp -i %SSH_KEY% gestao_rural\analise_financeira.py %SERVER%:%REMOTE%/gestao_rural/ 2>nul
scp -i %SSH_KEY% gestao_rural\gestao_projetos.py %SERVER%:%REMOTE%/gestao_rural/ 2>nul
scp -i %SSH_KEY% gestao_rural\ia_*.py %SERVER%:%REMOTE%/gestao_rural/ 2>nul
echo OK
echo.

echo [5/10] Transferindo Fixtures (Categorias)...
scp -i %SSH_KEY% gestao_rural\fixtures\categorias_animais.json %SERVER%:%REMOTE%/gestao_rural/fixtures/ 2>nul
echo OK
echo.

echo [6/10] Transferindo Commands...
scp -i %SSH_KEY% gestao_rural\management\commands\carregar_categorias.py %SERVER%:%REMOTE%/gestao_rural/management/commands/ 2>nul
echo OK
echo.

echo [7/10] Transferindo Templates (Todos)...
scp -i %SSH_KEY% templates\*.html %SERVER%:%REMOTE%/templates/ 2>nul
echo OK
echo.

echo [8/10] Transferindo Documentacao...
scp -i %SSH_KEY% *.md %SERVER%:%REMOTE%/ 2>nul
echo OK
echo.

echo [9/10] Carregando Categorias Pre-cadastradas...
ssh -i %SSH_KEY% %SERVER% "cd %REMOTE% && source venv/bin/activate && python manage.py carregar_categorias" 2>nul
echo OK
echo.

echo [10/10] Reiniciando Django...
ssh -i %SSH_KEY% %SERVER% "pkill -9 python && cd %REMOTE% && source venv/bin/activate && nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &" 2>nul
echo OK
echo.

echo ========================================
echo    ATUALIZACAO CONCLUIDA!
echo ========================================
echo.
echo NOVAS FUNCIONALIDADES:
echo  ✓ Identidade Visual (Azul Marinho + Terra)
echo  ✓ Formatacao Brasileira (1.000,00)
echo  ✓ 10 Categorias Pre-cadastradas
echo  ✓ Modulo Financeiro (5 submodulos)
echo  ✓ Gestao de Projetos Completa
echo  ✓ Login Profissional
echo  ✓ Inventario Melhorado
echo  ✓ Projecoes com Timeline
echo  ✓ Cards Elegantes
echo  ✓ 5 IAs Aprimoradas
echo.
echo 🌐 Teste agora:
echo    http://191.252.225.106
echo.
echo 📚 Leia o guia:
echo    GUIA_USUARIO_SISTEMA_MELHORADO.md
echo    RESUMO_TOTAL_MELHORIAS.md
echo.

pause

