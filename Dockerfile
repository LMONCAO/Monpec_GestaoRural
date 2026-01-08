# Use a imagem oficial do Python
FROM python:3.11-slim

# Definir diretÃ³rio de trabalho
WORKDIR /app

# Instalar dependÃªncias do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependÃªncias Python
COPY requirements_producao.txt .
RUN pip install --no-cache-dir -r requirements_producao.txt

# Copiar cÃ³digo do projeto
COPY . .

<<<<<<< HEAD
# Tornar entrypoint executável
RUN chmod +x entrypoint.sh
=======
# âœ… EXECUTAR collectstatic ANTES de finalizar a imagem
# Isso garante que todos os arquivos estÃ¡ticos estejam em STATIC_ROOT
# Usar --noinput para nÃ£o pedir confirmaÃ§Ã£o
# Nota: Pode falhar se nÃ£o houver variÃ¡veis de ambiente, mas isso Ã© OK
# O entrypoint.sh vai executar novamente com as variÃ¡veis corretas
RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp || echo "âš ï¸ collectstatic falhou no build, serÃ¡ executado no entrypoint..."
>>>>>>> 684d7dc9eeaad652e600bd3006f8f8ea7c4e5bfd

# Expor porta (Cloud Run usa a variÃ¡vel PORT)
EXPOSE 8080

<<<<<<< HEAD
# Usar entrypoint.sh que detecta automaticamente Fly.io ou GCP
# e executa collectstatic, migrations e inicia o servidor
ENTRYPOINT ["/app/entrypoint.sh"]
=======
# Usar entrypoint.sh para inicializaÃ§Ã£o
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando para iniciar o servidor (entrypoint.sh jÃ¡ configura tudo)
CMD ["/entrypoint.sh"]
>>>>>>> 684d7dc9eeaad652e600bd3006f8f8ea7c4e5bfd
