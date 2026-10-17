"""
ASGI config for project.
Combines Django ASGI application with FastAPI sub-application.
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Initialize Django ASGI application first so models and ORM are loaded
django_app = get_asgi_application()

from app.api import api_app  # noqa: E402

# Root ASGI application coordinating FastAPI at /api and Django at /
application = FastAPI(
    title="Sistema Híbrido Django + FastAPI",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

application.mount("/api", api_app)
application.mount("/", django_app)
