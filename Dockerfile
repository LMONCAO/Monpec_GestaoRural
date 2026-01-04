# Use a imagem oficial do Python
FROM python:3.11-slim

# Definir diretÃ³rio de trabalho
WORKDIR /app

# Instalar dependÃªncias do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependÃªncias Python
COPY requirements_producao.txt .
RUN pip install --no-cache-dir -r requirements_producao.txt

# Copiar cÃ³digo do projeto
COPY . .

# âœ… EXECUTAR collectstatic ANTES de finalizar a imagem
# Isso garante que todos os arquivos estÃ¡ticos estejam em STATIC_ROOT
RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp

# Expor porta
EXPOSE 8080

# Comando para iniciar o servidor
CMD exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 600