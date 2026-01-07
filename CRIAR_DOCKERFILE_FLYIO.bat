@echo off
chcp 65001 >nul
echo ========================================
echo Criando Dockerfile para Fly.io...
echo ========================================
echo.

(
echo # Dockerfile para Fly.io
echo # Use a imagem oficial do Python
echo FROM python:3.11-slim
echo.
echo # Instalar dependências do sistema
echo RUN apt-get update ^&^& apt-get install -y \
echo     postgresql-client \
echo     build-essential \
echo     libpq-dev \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo # Definir diretório de trabalho
echo WORKDIR /app
echo.
echo # Copiar requirements e instalar dependências Python
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo # Copiar código da aplicação
echo COPY . .
echo.
echo # Tornar entrypoint executável
echo COPY entrypoint.sh /entrypoint.sh
echo RUN chmod +x /entrypoint.sh
echo.
echo # Expor porta (Fly.io usa porta 8080 por padrão)
echo EXPOSE 8080
echo.
echo # Comando de entrada
echo ENTRYPOINT ["/entrypoint.sh"]
) > Dockerfile

if exist Dockerfile (
    echo ✅ Dockerfile criado com sucesso!
    echo.
    echo ========================================
    echo Conteúdo do Dockerfile:
    echo ========================================
    type Dockerfile
    echo.
    echo ========================================
    echo ✅ Pronto! Agora você pode fazer deploy no Fly.io
    echo ========================================
) else (
    echo ❌ Erro ao criar Dockerfile
    exit /b 1
)

pause
