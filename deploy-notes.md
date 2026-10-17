# Guía de Arquitectura, Despliegue y Operaciones CI/CD

**Sistema:** Plataforma Híbrida Django 5 + FastAPI + PostgreSQL en Docker  
**Rama:** `ci-setup`  
**Entorno de Ejecución:** Contenedores OCI / Docker Engine / Python 3.10-alpine  

---

## 1. Arquitectura General del Sistema

El sistema implementa una arquitectura monolítica híbrida orientada al rendimiento, integridad y mantenibilidad:

- **Capa Web y Administración (Django 5.2.18)**: Gestiona el modelo de datos relacional, el motor de migraciones con restricciones DDL nativas, las vistas basadas en clases (`IndexView`, `PersonaApiBridgeView`) y el servicio de archivos estáticos.
- **Capa de API de Alto Rendimiento (FastAPI 0.115.0 + Pydantic 2.9.2)**: Montada como sub-aplicación ASGI bajo la ruta `/api/v1/`, proporcionando serialización estricta, documentación OpenAPI interactiva (`/docs`) y validación de esquemas en tiempo de compilación/ejecución.
- **Servidor ASGI de Producción (Uvicorn 0.30.6)**: Orquesta tanto el ciclo de vida de Django como de FastAPI en un único bucle de eventos asíncrono sobre el puerto 8000.
- **Persistencia (PostgreSQL 15)**: Base de datos relacional con comprobaciones de integridad estrictas (`CheckConstraint`) a nivel de esquema DDL.
- **Contenedorización Segura**: Imagen base `python:3.10-alpine` hardened, con paquetes de sistema actualizados vía `apk` y eliminación de vulnerabilidades conocidas.

---

## 2. Guía de Despliegue en Entorno de Pruebas / Servidor Externo

Instrucciones para desplegar el sistema en un host externo o servidor de staging replicando un entorno de producción.

### Requisitos Previos
- Docker Engine 24.0+ y Docker Compose v2.0+.
- Git instalado (o transferencia manual de artefacto).
- Puertos `8000` (web) y `5432` (db) disponibles.

### Paso 1: Creación del Directorio de Despliegue
```powershell
mkdir C:\despliegue_produccion_django
cd C:\despliegue_produccion_django
```

### Paso 2: Obtención del Código o Descarga del Artefacto

#### Opción A (Clonación directa de repositorio - Recomendada):
```bash
git clone -b ci-setup https://github.com/TU_USUARIO/TU_REPOSITORIO.git .
```

#### Opción B (Uso del artefacto empaquetado por GitHub Actions):
1. Descargar el artefacto `django-app-artifact.zip` generado por el pipeline de GitHub Actions.
2. Descomprimir el contenido en el directorio de despliegue obteniendo `django-app-image.tar`.
3. Cargar la imagen directamente en el motor Docker local:
   ```bash
   docker load -i django-app-image.tar
   ```

### Paso 3: Configuración de Variables de Entorno
Crear el archivo `.env` en la raíz del despliegue basándose en `.env.example`:
```env
DEBUG=False
SECRET_KEY=clave-secreta-produccion-alta-entropia-minimo-50-caracteres
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
POSTGRES_DB=practican3
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Paso 4: Ejecución con Docker Compose
Iniciar la infraestructura completa en segundo plano:
```bash
docker compose up -d --build
```

### Paso 5: Verificación de Estado y Logs
Comprobar el aprovisionamiento correcto y la ejecución de migraciones automáticas:
```bash
docker compose ps
docker compose logs -f web
```

Salida esperada en consola:
```text
==> Esperando a que PostgreSQL esté disponible...
Probando conexión con db:5432...
PostgreSQL disponible en db:5432 tras 1 intento(s).
==> Aplicando migraciones de Django...
Operations to perform:
  Apply all migrations: admin, app, auth, contenttypes, sessions
Running migrations:
  Applying app.0001_initial... OK
==> Ejecutando comando del contenedor: uvicorn project.asgi:application --host 0.0.0.0 --port 8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 3. Pipeline de Integración y Despliegue Continuo (CI/CD)

El archivo `.github/workflows/ci.yml` automatiza el ciclo de vida del software mediante dos etapas secuenciales obligatorias:

```text
[ Desarrollador ]
       │
       ▼ (git push / pull request)
[ GitHub Repository ]
       │
       ▼ (Workflow Trigger: ci.yml)
[ GitHub Actions Runner ]
       │
       ├─► Job 1: Pruebas Automatizadas y Migraciones
       │     ├─ Servicio PostgreSQL 15 en contenedor (postgres:15-alpine)
       │     ├─ Entorno Python 3.10 con caché pip activada
       │     ├─ Instalación de dependencias (requirements.txt)
       │     ├─ Ejecución de migraciones DDL ('python manage.py migrate')
       │     └─ Ejecución de suite de pruebas ('python manage.py test -v 2') [100% OK]
       │
       ▼ (requires: test con 0 fallos)
       ├─► Job 2: Construcción, Empaquetado y Publicación Docker
             ├─ Configuración de Docker Buildx
             ├─ Compilación de imagen OCI ('docker build -t django-app:ci-build .')
             ├─ Empaquetado binario ('docker save -o django-app-image.tar')
             ├─ Almacenamiento seguro del artefacto en GitHub Actions
             └─ Etiquetado y publicación simulada en registro de imágenes
```

### Especificación de Jobs en GitHub Actions

1. **`test`**:
   - Provisiona un contenedor de servicio PostgreSQL 15 con comprobación de salud activa (`pg_isready`).
   - Aplica migraciones reales sobre PostgreSQL para garantizar paridad absoluta con producción.
   - Ejecuta las 10 pruebas automatizadas que verifican modelos, API REST FastAPI, vistas Django y manejo de restricciones de integridad.
2. **`build-docker`**:
   - Bloqueado por `needs: test`. Si una sola prueba falla, la construcción de la imagen se aborta de inmediato.
   - Genera una imagen hermética con base `python:3.10-alpine`.
   - Empaqueta la imagen construida en un archivo `.tar` disponible para auditoría y despliegue desacoplado.

---

## 4. Estrategia de Validación de Datos en Tres Capas

Para garantizar máxima resiliencia e integridad de datos, el sistema implementa defensa en profundidad:

1. **Capa 1: Validación en Cliente (Frontend)**
   - Expresiones regulares en tiempo real para nombres completos (2 a 4 palabras alfabéticas, capitalización formal).
   - Selector de fechas con restricción nativa (`min="1970-01-01"`, `max="2100-12-31"`).
   - Mensajería Toast dinámica en español con bloqueo de envíos anómalos.
2. **Capa 2: Validación en Aplicación (Backend)**
   - Serializadores Pydantic v2 (`PersonaCreateSerializer`, `PersonaOutSerializer`) con validadores `@field_validator`.
   - Validadores nativos de Django a nivel de modelo (`RegexValidator`, `MinValueValidator`, `MaxValueValidator`).
   - Respuestas HTTP estructuradas con códigos estandarizados (`200 OK`, `201 Created`, `400 Bad Request`, `405 Method Not Allowed`, `422 Unprocessable Entity`).
3. **Capa 3: Restricciones Nativas en Base de Datos (DDL)**
   - `CheckConstraint(check=Q(fecha_nacimiento__gte='1970-01-01'))`.
   - `CheckConstraint(check=Q(fecha_nacimiento__lte='2100-12-31'))`.
   - `CheckConstraint(check=Q(nombre__regex=r'^[A-ZÁÉÍÓÚÑa-záéíóúñ]+( [A-ZÁÉÍÓÚÑa-záéíóúñ]+){1,3}$'))`.

---

## 5. Medidas de Seguridad y Buenas Prácticas

- **Gestión de Credenciales**: Parámetros sensibles (`SECRET_KEY`, `POSTGRES_PASSWORD`, hosts de base de datos) desacoplados en variables de entorno `.env` ignoradas por el control de versiones.
- **Imagen Base Hardened**: Uso de Alpine Linux (`python:3.10-alpine`), eliminando paquetes heredados vulnerables presentes en distribuciones Debian estándar.
- **Zero Comments**: Código de aplicación limpio y conciso, sin comentarios residuales ni exposición de lógica interna sensible.
- **Prevención de Ataques Web**: Protección CSRF integrada en vistas Django, encabezados de seguridad HTTP configurados en settings, y validación estricta de métodos HTTP en la API.
