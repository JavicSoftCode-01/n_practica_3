from fastapi import APIRouter, FastAPI
from app.models import Persona
from app.schemas import PersonaCreate, PersonaOut

api_app = FastAPI(
    title="API Personas Serializable",
    description="API RESTful de Personas con validación estricta",
    version="1.0.0",
)

router = APIRouter()


@router.get("/personas", response_model=list[PersonaOut], status_code=200)
def listar_personas():
    """
    Retorna la lista de todas las personas registradas, ordenadas por ID descendente.
    """
    personas = Persona.objects.all().order_by('-id')
    return [PersonaOut.model_validate(p) for p in personas]


@router.post("/personas", response_model=PersonaOut, status_code=201)
def crear_persona(payload: PersonaCreate):
    """
    Valida y registra una nueva persona en PostgreSQL mediante el ORM de Django.
    """
    persona = Persona(
        nombres_completos=payload.nombres_completos,
        fecha_nacimiento=payload.fecha_nacimiento,
    )
    persona.save()
    return PersonaOut.model_validate(persona)


# Registramos el router tanto con prefijo base como con /api para compatibilidad total
api_app.include_router(router)
api_app.include_router(router, prefix="/api")
