#!/bin/bash

# TESTE MÍNIMO: Servidor HTTP simples para verificar se container funciona
export PORT=${PORT:-8080}

echo "🧪 TESTE MÍNIMO: Iniciando servidor HTTP simples..."
echo "📍 Porta: $PORT"

# Verificar se Python está funcionando
python3 -c "print('✅ Python OK')" || exit 1

# Iniciar servidor HTTP simples com Python
cd /app
python3 -m http.server $PORT --bind 0.0.0.0 || {
    echo "❌ Servidor HTTP falhou, tentando alternativa..."

    # Fallback: usar netcat ou similar se disponível
    if command -v nc >/dev/null 2>&1; then
        echo "📡 Usando netcat como servidor..."
        while true; do
            echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nMONPEC OK - Porta $PORT" | nc -l -p $PORT -q 1
        done
    else
        echo "❌ Nenhum servidor disponível"
        exit 1
    fi
}
