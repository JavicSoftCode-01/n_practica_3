# Imagen base oficial de Python 3.10 requerida por la guía
FROM python:3.10

# Prevención de archivos .pyc y configuración de salida sin búfer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalación de dependencias del proyecto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia del código fuente al contenedor
COPY . /app/

# Asegurar terminaciones de línea Unix y permisos de ejecución en entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exposición del puerto estándar
EXPOSE 8000

# Punto de entrada explícito que aplica migraciones
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para iniciar el servidor ASGI
CMD ["uvicorn", "project.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
