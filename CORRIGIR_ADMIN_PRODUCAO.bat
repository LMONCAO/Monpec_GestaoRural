@echo off
echo ============================================================
echo CORREÇÃO DO USUÁRIO ADMIN - PRODUÇÃO
echo ============================================================
echo.
echo Este script vai corrigir o usuário admin no banco de dados
echo de produção (monpec.com.br)
echo.
echo Credenciais:
echo   Usuario: admin
echo   Senha: L6171r12@@
echo.
pause

python corrigir_admin_producao.py

echo.
echo ============================================================
echo Processo concluido!
echo ============================================================
pause






























