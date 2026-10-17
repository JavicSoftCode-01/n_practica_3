import re
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

REGEX_NOMBRES = r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+( [A-Za-zÁÉÍÓÚáéíóúÑñÜü]+){1,3}$'
FECHA_MINIMA = date(1970, 1, 1)
FECHA_MAXIMA = date(2100, 12, 31)


class PersonaCreate(BaseModel):
    nombres_completos: str = Field(
        ...,
        min_length=3,
        max_length=60,
        description="2 a 4 palabras, solo letras y espacios simples, máx 60 caracteres.",
    )
    fecha_nacimiento: date = Field(
        ...,
        description="Fecha comprendida entre 1970-01-01 y 2100-12-31.",
    )

    @field_validator('nombres_completos')
    @classmethod
    def validar_nombres_completos(cls, v: str) -> str:
        if not v:
            raise ValueError("El campo nombres completos no puede estar vacío.")
        v_stripped = v.strip()
        if len(v_stripped) > 60:
            raise ValueError("El campo nombres completos no puede superar 60 caracteres.")
        if not re.match(REGEX_NOMBRES, v_stripped):
            raise ValueError(
                "El campo nombres completos solo debe contener letras del español "
                "separadas por un único espacio simple, entre 2 y 4 palabras."
            )
        words = v_stripped.split(' ')
        if len(words) < 2 or len(words) > 4:
            raise ValueError("Debe ingresar entre 2 y 4 palabras (nombres y apellidos).")
        return v_stripped

    @field_validator('fecha_nacimiento')
    @classmethod
    def validar_fecha_nacimiento(cls, v: date) -> date:
        if v < FECHA_MINIMA or v > FECHA_MAXIMA:
            raise ValueError(
                f"La fecha de nacimiento debe estar comprendida entre {FECHA_MINIMA} y {FECHA_MAXIMA}."
            )
        return v


class PersonaOut(BaseModel):
    id: int
    nombres_completos: str
    fecha_nacimiento: date
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
