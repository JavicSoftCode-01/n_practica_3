"""
Módulo de Serializadores para la API RESTful (FastAPI / Django).

En arquitecturas modernas basadas en FastAPI, los modelos de Pydantic cumplen el rol
de serializadores y deserializadores de alto rendimiento:

1. PersonaCreate (PersonaCreateSerializer):
   - Serializador de entrada (Input Deserializer).
   - Valida reglas de negocio: nombres entre 2 y 4 palabras, sin caracteres especiales,
     y fecha de nacimiento entre 1970 y 2100.

2. PersonaOut (PersonaOutSerializer):
   - Serializador de salida (Output Serializer).
   - Serializa objetos ORM de Django (from_attributes=True) hacia JSON estructurado.
"""

from app.schemas import PersonaCreate, PersonaOut

# Aliases explícitos para claridad semántica y convención de nombres
PersonaCreateSerializer = PersonaCreate
PersonaOutSerializer = PersonaOut

__all__ = [
    'PersonaCreate',
    'PersonaOut',
    'PersonaCreateSerializer',
    'PersonaOutSerializer',
]
