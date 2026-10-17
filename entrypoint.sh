#!/bin/sh
set -e

echo "==> Esperando a que PostgreSQL esté disponible..."

# Espera activa a que el socket de PostgreSQL acepte conexiones
python - << 'EOF'
import socket
import time
import os
import sys

host = os.environ.get('DB_HOST', 'localhost')
port = int(os.environ.get('DB_PORT', 5432))

print(f"Probando conexión con {host}:{port}...")
for attempt in range(1, 31):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"PostgreSQL disponible en {host}:{port} tras {attempt} intento(s).")
            sys.exit(0)
    except (socket.error, OSError):
        time.sleep(1)

print(f"ERROR: No se pudo conectar a PostgreSQL en {host}:{port} tras 30 segundos.")
sys.exit(1)
EOF

echo "==> Aplicando migraciones de Django..."
python manage.py migrate --noinput

echo "==> Ejecutando comando del contenedor: $@"
exec "$@"
