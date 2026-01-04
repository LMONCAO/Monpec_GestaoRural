@echo off
chcp 65001 >nul
echo Criando Dockerfile...

(
echo # Use a imagem oficial do Python
echo FROM python:3.11-slim
echo.
echo # Definir diretório de trabalho
echo WORKDIR /app
echo.
echo # Instalar dependências do sistema
echo RUN apt-get update ^&^& apt-get install -y \
echo     gcc \
echo     postgresql-client \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo # Copiar requirements e instalar dependências Python
echo COPY requirements_producao.txt .
echo RUN pip install --no-cache-dir -r requirements_producao.txt
echo.
echo # Copiar código do projeto
echo COPY . .
echo.
echo # Copiar e configurar script de entrada
echo COPY entrypoint.sh /app/entrypoint.sh
echo RUN chmod +x /app/entrypoint.sh
echo.
echo # ✅ EXECUTAR collectstatic DURANTE O BUILD (com variáveis mínimas)
echo # Isso garante que os arquivos estáticos estejam na imagem
echo # Se falhar, será executado novamente no startup via entrypoint.sh
echo ENV SECRET_KEY=dummy-key-for-build
echo RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp ^|^| echo "⚠️ collectstatic falhou no build, será executado no startup..."
echo.
echo # Expor porta
echo EXPOSE 8080
echo.
echo # Usar script de entrada que executa collectstatic antes de iniciar
echo # Isso garante que os arquivos estáticos estejam sempre atualizados
echo CMD ["/app/entrypoint.sh"]
) > Dockerfile

if exist Dockerfile (
    echo ✅ Dockerfile criado com sucesso!
    echo.
    echo Verificando conteúdo...
    type Dockerfile
) else (
    echo ❌ Erro ao criar Dockerfile
    exit /b 1
)

pause
