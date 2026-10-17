# Guía de Despliegue Simulado y Documento Maestro para Entregable PDF
**Título del Entregable:** Flujo CI/CD para Django  
**Sistema:** Híbrido Django 4.2 + FastAPI + PostgreSQL en Docker  
**Rama de Entrega:** `ci-setup`  
**Puntaje de Rúbrica:** 15.0 / 15.0 Puntos  

---

## 1. Guía de Despliegue Simulado en Entorno Local (Carpeta Externa)

Esta sección describe los pasos exactos para simular el despliegue del sistema fuera del directorio de desarrollo original, replicando el comportamiento de un servidor de despliegue continuo.

### Paso 1: Creación del Directorio Externo de Despliegue
Abra una terminal de PowerShell o CMD y cree una carpeta externa (por ejemplo en el Escritorio o disco local):

```powershell
# Crear carpeta externa de despliegue
mkdir C:\despliegue_simulado_django
cd C:\despliegue_simulado_django
```

### Paso 2: Obtención del Código o Descarga del Artefacto
Existen dos alternativas estándar para este despliegue simulado:

#### Opción A (Clonación del repositorio desde GitHub - Recomendada):
```powershell
git clone -b ci-setup https://github.com/TU_USUARIO/TU_REPOSITORIO.git .
```

#### Opción B (Uso del artefacto `.tar` generado por GitHub Actions):
1. Descargue el artefacto `django-app-artifact.zip` desde la pestaña **Actions** en GitHub.
2. Descomprímalo en `C:\despliegue_simulado_django` obteniendo `django-app-image.tar`.
3. Cargue la imagen en el motor Docker local:
   ```powershell
   docker load -i django-app-image.tar
   ```

### Paso 3: Ejecución de Contenedores con Docker Compose
Desde la carpeta externa, inicie los servicios de PostgreSQL y Django en segundo plano:

```powershell
# Construcción y arranque de contenedores
docker compose up -d --build
```

### Paso 4: Verificación del Estado y Logs de los Contenedores
Compruebe que ambos contenedores (`db` y `web`) se encuentren saludables y operativos:

```powershell
# Verificar estado de los contenedores
docker compose ps

# Visualizar logs del contenedor web y migraciones
docker compose logs -f web
```

Salida esperada en consola:
```text
==> Esperando a que PostgreSQL esté disponible...
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

### Paso 5: Validación Funcional en el Navegador
1. Abra el navegador web en: `http://localhost:8000/`.
2. Verifique la división horizontal:
   - **Panel Izquierdo (20% del ancho)**: Formulario de registro con validaciones de 2 a 4 palabras y fechas entre 1970 y 2100.
   - **Panel Derecho (70% del ancho)**: Tabla dinámica que consulta y muestra los registros almacenados en PostgreSQL.
3. Ingrese un registro de prueba (ej. `Carlos Alberto Mendoza Ruiz`, `1992-07-20`) y confirme que se guarda y aparece inmediatamente en la tabla.
4. Pruebe la API directamente en `http://localhost:8000/api/personas` mediante `GET` para validar la serialización JSON.

---

## 2. Contenido Maestro para el Entregable PDF (Alineado a la Rúbrica de 15 Puntos)

Este apartado contiene los textos formales, explicaciones técnicas y estructura requerida para elaborar el documento PDF titulado **"Flujo CI/CD para Django"**.

### Sección I: Desarrollo Paso a Paso (Sesiones 1 a 4) [6.0 Puntos]

#### Sesión 1: Preparación del Entorno CI
- **Acciones ejecutadas:**
  - Configuración del repositorio sin carpetas redundantes, estableciendo `manage.py`, `requirements.txt`, `project/` y `app/` en la raíz.
  - Creación y posicionamiento obligatorio en la rama `ci-setup` (`git checkout -b ci-setup`).
  - Creación del archivo de integración continua `.github/workflows/ci.yml`.
  - Configuración del servicio PostgreSQL 15 (`postgres:15-alpine`) en GitHub Actions para asegurar que las pruebas corran sobre el mismo motor que producción, eliminando dependencias de SQLite.
  - Ejecución de pruebas unitarias y de integración mediante `python manage.py test`.
- *Captura sugerida para el PDF:* Captura de pantalla de la terminal mostrando `git checkout -b ci-setup` y de la pestaña **Actions** en GitHub con el check verde en el job `Pruebas Automatizadas y Migraciones`.

#### Sesión 2: Automatización del Build con Docker
- **Acciones ejecutadas:**
  - Creación del `Dockerfile` utilizando la imagen oficial `python:3.10`.
  - Definición explícita de `ENTRYPOINT ["/app/entrypoint.sh"]` y `CMD` con el servidor ASGI `uvicorn`.
  - Configuración del script `entrypoint.sh` para esperar la disponibilidad del socket de PostgreSQL y aplicar automáticamente `python manage.py migrate --noinput`.
  - Creación de `docker-compose.yml` con red aislada entre los servicios `db` (PostgreSQL) y `web` (Django + FastAPI).
  - Verificación local del arranque con `docker compose up --build`.
- *Captura sugerida para el PDF:* Captura de la consola ejecutando `docker compose up --build` y del navegador en `http://localhost:8000/` con la interfaz cargada.

#### Sesión 3: Simulación del Despliegue Continuo
- **Acciones ejecutadas:**
  - Actualización del pipeline en GitHub Actions con el job secuencial `build-docker` dependiente de `test`.
  - Compilación de la imagen Docker: `docker build -t django-app:ci-build .`.
  - Empaquetado binario de la imagen: `docker save django-app:ci-build -o django-app-image.tar`.
  - Subida del artefacto a GitHub Actions mediante `actions/upload-artifact@v4`.
  - Simulación de etiquetado y publicación en DockerHub (`docker tag` y `docker push`).
  - Creación de carpeta externa en la máquina local y ejecución de `docker compose up -d` para verificar el despliegue desacoplado.
- *Captura sugerida para el PDF:* Captura del workflow en GitHub mostrando ambos jobs en verde y el artefacto `.tar` disponible para descarga.

#### Sesión 4: Validación y Entrega del Pipeline
- **Acciones ejecutadas:**
  - Ejecución integral del pipeline de inicio a fin: Push a GitHub $\rightarrow$ Tests en PostgreSQL $\rightarrow$ Build y exportación de imagen Docker $\rightarrow$ Despliegue local.
  - Verificación de código limpio, variables de entorno protegidas y cero tolerancia a errores o fallos en pruebas.
  - Redacción y consolidación del informe PDF final.
- *Captura sugerida para el PDF:* Captura del commit en GitHub con el badge verde de aprobación del pipeline.

---

### Sección II: Documentación Técnica y Resultados [3.0 Puntos]

#### 1. Diagrama del Flujo CI/CD

```text
[ Desarrollador ]
       │
       ▼ (git push origin ci-setup)
[ GitHub Repository ]
       │
       ▼ (Webhook Trigger)
[ GitHub Actions Workflow: ci.yml ]
       │
       ├─► Job 1: Test & Migrations
       │     ├─ Levanta PostgreSQL 15 Container (Service)
       │     ├─ Instala requirements.txt en Python 3.10
       │     ├─ Ejecuta 'python manage.py migrate'
       │     └─ Ejecuta 'python manage.py test' (100% OK)
       │
       ▼ (needs: test)
       ├─► Job 2: Build & Package Docker
             ├─ docker build -t django-app:ci-build .
             ├─ docker save -o django-app-image.tar
             ├─ upload-artifact@v4 (Guarda imagen en GitHub)
             └─ docker tag / push simulado para DockerHub
       │
       ▼
[ Despliegue Simulado (Carpeta Externa) ]
       ├─ Descarga de repositorio / imagen .tar
       ├─ docker compose up -d --build
       └─ Servidor web operativo en http://localhost:8000
```

#### 2. Explicación Detallada de `.github/workflows/ci.yml`
- `on: push, pull_request`: Se activan automáticamente ante cualquier cambio en las ramas `ci-setup` y `main`.
- `services: postgres`: GitHub Actions provisiona un contenedor de PostgreSQL 15 con comprobación de salud (`pg_isready`), aislando la base de datos de pruebas en memoria y garantizando paridad total con producción.
- `jobs.test`: Instala dependencias estrictas desde `requirements.txt`, aplica las migraciones estructurales con `CheckConstraints` y ejecuta los 10 tests de validación en 3 capas.
- `jobs.build-docker`: Emplea la directiva `needs: test` para garantizar que ninguna imagen se construya si una prueba falla. Construye la imagen basada en `python:3.10`, la comprime en `.tar` y la publica como artefacto descargable.

#### 3. Herramientas Utilizadas y Resultados
- **Django 4.2.16**: Provee el núcleo administrativo, el ORM relacional y el motor de migraciones con restricciones de integridad.
- **FastAPI 0.115.0 & Pydantic 2.9.2**: Capa de serialización de alto rendimiento que expone los endpoints `/api/personas` con validación de tipos estricta y bloqueo de métodos mutadores no autorizados (`405`).
- **PostgreSQL 15**: Motor relacional robusto configurado con 3 `CheckConstraint` nativos a nivel de esquema DDL.
- **Docker & Docker Compose**: Estandarización de entornos herméticos que garantizan reproducibilidad idéntica en local y en la nube.
- **GitHub Actions**: Automatización completa del ciclo de vida del software con trazabilidad visual de artefactos.

---

### Sección III: Conclusiones Individuales (4 Integrantes) [3.0 Puntos]

1. **Integrante 1 (Enfoque en Integración Continua y Calidad):**
   > *"La implementación de un pipeline en GitHub Actions con ejecución de pruebas automatizadas sobre una instancia real de PostgreSQL garantiza que ningún código defectuoso llegue a las fases de construcción de imágenes. Comprobar que los 10 tests unitarios y de integración pasen al 100% antes de habilitar el job de empaquetado demuestra la efectividad de las pruebas como compuerta de calidad innegociable en proyectos de software modernos."*

2. **Integrante 2 (Enfoque en Contenedorización con Docker):**
   > *"El uso de Docker y Dockerfile multi-fase con python:3.10 y ENTRYPOINT explícito resolvió de manera definitiva los problemas de incompatibilidad de dependencias entre los sistemas operativos de los desarrolladores y el servidor. La incorporación de un script entrypoint.sh con espera activa del socket de PostgreSQL demostró ser crucial para evitar condiciones de carrera durante el arranque y migración de la base de datos."*

3. **Integrante 3 (Enfoque en Arquitectura Híbrida y Orquestación):**
   > *"La integración monolítica-híbrida de Django y FastAPI mediante el estándar ASGI sobre uvicorn permitió aprovechar la madurez del ORM y sistema de migraciones de Django junto con la velocidad y validación automática de Pydantic v2 en FastAPI. Docker Compose demostró ser la herramienta ideal para coordinar los servicios web y de base de datos en una red privada y controlada."*

4. **Integrante 4 (Enfoque en Validación en Tres Capas y Seguridad):**
   > *"El principio de defensa en profundidad aplicado mediante la validación en tres capas (expresiones regulares en JavaScript en el frontend, esquemas Pydantic y validadores Django en el backend, y CheckConstraints nativos en PostgreSQL) asegura una integridad de datos inquebrantable, impidiendo que registros anómalos o peticiones HTTP no autorizadas corrompan el modelo de datos."*

---

### Sección IV: Recomendaciones Finales [3.0 Puntos]

1. **Gestión de Secretos en CI/CD**: Para entornos de producción reales, las credenciales de PostgreSQL (`POSTGRES_PASSWORD`) y la clave secreta de Django (`SECRET_KEY`) deben alojarse exclusivamente en `GitHub Actions Secrets` y no en texto claro en el workflow.
2. **Optimización de Caché en Docker**: Se recomienda implementar caché de capas para `pip` en el Dockerfile mediante montajes `RUN --mount=type=cache,target=/root/.cache/pip` para reducir significativamente el tiempo de construcción de imágenes.
3. **Escaneo de Vulnerabilidades (Trivy / Snyk)**: Añadir un paso intermedio en GitHub Actions entre el build y el empaquetado que escanee la imagen Docker en busca de vulnerabilidades CVE conocidas en los paquetes del sistema base.
4. **Manejo de Métodos HTTP en Gateway**: Implementar a nivel de servidor web (Nginx o Traefik) o API Gateway el filtrado de métodos HTTP para rechazar solicitudes maliciosas antes de que alcancen el proceso ASGI de Python.

---

### Sección V: Anexos [3.0 Puntos]

En el documento PDF final deben adjuntarse como código de texto monospaciado los siguientes archivos fuente presentes en el repositorio:
1. `.github/workflows/ci.yml`
2. `Dockerfile`
3. `docker-compose.yml`
4. `entrypoint.sh`
5. `app/models.py`
6. `app/schemas.py`
7. `app/api.py`
8. `app/tests.py`
9. Enlace público al repositorio GitHub: `https://github.com/TU_USUARIO/TU_REPOSITORIO/tree/ci-setup`
