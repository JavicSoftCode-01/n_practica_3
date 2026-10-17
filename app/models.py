import datetime
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

REGEX_NOMBRES_COMPLETOS = r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+( [A-Za-zÁÉÍÓÚáéíóúÑñÜü]+){1,3}$'
FECHA_MINIMA = datetime.date(1970, 1, 1)
FECHA_MAXIMA = datetime.date(2100, 12, 31)

nombres_validator = RegexValidator(
    regex=REGEX_NOMBRES_COMPLETOS,
    message=(
        "El campo nombres completos solo debe contener letras del español "
        "separadas por un único espacio simple, con un mínimo de 2 palabras "
        "y un máximo de 4 palabras."
    ),
    code="invalid_nombres_completos",
)


def validate_fecha_nacimiento(value):
    if value is None:
        raise ValidationError("La fecha de nacimiento es obligatoria.")
    if value < FECHA_MINIMA or value > FECHA_MAXIMA:
        raise ValidationError(
            f"La fecha de nacimiento debe estar comprendida entre {FECHA_MINIMA} y {FECHA_MAXIMA}."
        )


class Persona(models.Model):
    nombres_completos = models.CharField(
        max_length=60,
        validators=[nombres_validator],
        help_text="2 a 4 palabras, solo letras y espacios simples, máx 60 caracteres.",
    )
    fecha_nacimiento = models.DateField(
        validators=[validate_fecha_nacimiento],
        help_text="Fecha comprendida entre 1970-01-01 y 2100-12-31.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['-id']
        constraints = [
            models.CheckConstraint(
                check=models.Q(nombres_completos__regex=REGEX_NOMBRES_COMPLETOS),
                name='check_nombres_completos_regex',
            ),
            models.CheckConstraint(
                check=models.Q(fecha_nacimiento__gte=FECHA_MINIMA),
                name='check_fecha_nacimiento_gte_1970',
            ),
            models.CheckConstraint(
                check=models.Q(fecha_nacimiento__lte=FECHA_MAXIMA),
                name='check_fecha_nacimiento_lte_2100',
            ),
        ]

    def clean(self):
        super().clean()
        if self.nombres_completos:
            val = self.nombres_completos.strip()
            if len(val) > 60:
                raise ValidationError(
                    {'nombres_completos': "La longitud no puede exceder 60 caracteres."}
                )
            if not re.match(REGEX_NOMBRES_COMPLETOS, val):
                raise ValidationError(
                    {
                        'nombres_completos': (
                            "Debe contener solo letras y entre 2 y 4 palabras "
                            "separadas por un espacio simple."
                        )
                    }
                )
            words = val.split(' ')
            if len(words) < 2 or len(words) > 4:
                raise ValidationError(
                    {'nombres_completos': "Debe contener entre 2 y 4 palabras."}
                )

        if self.fecha_nacimiento:
            if (
                self.fecha_nacimiento < FECHA_MINIMA
                or self.fecha_nacimiento > FECHA_MAXIMA
            ):
                raise ValidationError(
                    {
                        'fecha_nacimiento': (
                            f"Fecha fuera del rango permitido ({FECHA_MINIMA} a {FECHA_MAXIMA})."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombres_completos} ({self.fecha_nacimiento})"
