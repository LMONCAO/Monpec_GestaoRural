# Use a imagem oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements_producao.txt .
RUN pip install --no-cache-dir -r requirements_producao.txt

# Copiar código do projeto
COPY . .

# Tornar entrypoint executável
RUN chmod +x entrypoint.sh

# Expor porta
EXPOSE 8080

# Usar entrypoint.sh que detecta automaticamente Fly.io ou GCP
# e executa collectstatic, migrations e inicia o servidor
ENTRYPOINT ["/app/entrypoint.sh"]
