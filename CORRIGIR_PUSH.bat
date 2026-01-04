@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Corrigir Push - Remover arquivo secreto

echo ========================================
echo   CORRIGINDO PUSH DO GIT
echo ========================================
echo.
echo Removendo github-actions-key.json do Git...
git rm --cached github-actions-key.json 2>nul
echo.
echo Adicionando .gitignore atualizado...
git add .gitignore
echo.
echo Fazendo commit da correcao...
git commit -m "Remover arquivo secreto github-actions-key.json do Git"
echo.
echo Fazendo push...
git push origin master
echo.
echo ✅ Correcao aplicada!
echo.
echo O arquivo github-actions-key.json agora esta no .gitignore
echo e nao sera mais commitado.
echo.
pause
