@echo off
chcp 65001 >nul
cd /d "%~dp0"
git status
git add -A
git commit -m "Preparar bootstrap do GCP e ajustes de deploy"
git push

