# Dockerfile para Google Cloud Run
# Otimizado para Django

FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements_producao.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_producao.txt

# Copiar código da aplicação
COPY . .

# Definir SECRET_KEY temporário para collectstatic (será sobrescrito em runtime)
ENV SECRET_KEY=temp-key-for-collectstatic

# Coletar arquivos estáticos usando settings_gcp
# Isso garante que STATICFILES_DIRS seja usado e todos os arquivos sejam coletados
RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp || true

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8080

# Comando para iniciar
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 sistema_rural.wsgi:application

