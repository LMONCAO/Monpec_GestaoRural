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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Não. EXECUTAR collectstatic ANTES de finalizar a imagem
# Isso garante que todos os arquivos estáticos estejam em STATIC_ROOT
# Usar --noinput para não pedir confirmação
# Nota: Pode falhar se não houver variáveis de ambiente, mas isso é OK
# O entrypoint.sh vai executar novamente com as variáveis corretas
RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp || echo "Aviso: collectstatic falhou no build, será executado no entrypoint..."

# Expor porta (Cloud Run usa a variável PORT)
EXPOSE 8080

# Usar entrypoint.sh para inicialização
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando para iniciar o servidor (entrypoint.sh já configura tudo)
# Atualizado em 2026-01-10 para forçar rebuild
CMD ["/entrypoint.sh"]
