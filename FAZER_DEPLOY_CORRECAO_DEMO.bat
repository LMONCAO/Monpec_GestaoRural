@echo off
echo ========================================
echo Deploy - Correcao Formulario Demo
echo ========================================
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0"

echo Verificando status do Git...
git status --short

echo.
echo Adicionando alteracoes...
git add gestao_rural/views.py

echo.
echo Fazendo commit...
git commit -m "Fix: Melhorar robustez do cadastro de usuario demonstracao no Google Cloud

- Adicionar commit explicito apos criar/atualizar usuario
- Implementar retry com delay ao buscar usuario apos criacao
- Melhorar tratamento de erros de banco de dados
- Adicionar fallback para erro de integridade (usuario duplicado)
- Melhorar mensagens de erro para diferentes tipos de falha"

echo.
echo Fazendo push para trigger do deploy...
git push origin master

echo.
echo ========================================
echo Deploy iniciado!
echo ========================================
echo.
echo O deploy sera executado automaticamente via GitHub Actions.
echo Acompanhe o progresso em: https://github.com/[seu-usuario]/[seu-repo]/actions
echo.
pause
