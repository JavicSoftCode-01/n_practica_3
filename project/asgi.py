import os
from pathlib import Path
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django_app = get_asgi_application()

from app.api import api_app

application = FastAPI(
    title="Sistema Híbrido Django + FastAPI",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / 'app' / 'static'
if static_dir.exists():
    application.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

application.mount("/api", api_app)
application.mount("/", django_app)
