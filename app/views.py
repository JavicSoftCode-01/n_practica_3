import json
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError as PydanticValidationError

from app.models import Persona
from app.schemas import PersonaCreate, PersonaOut


def index(request):
    """
    Renderiza la vista principal dividida horizontalmente:
    20% formulario (izquierda) y 70% tabla de datos (derecha).
    """
    return render(request, 'app/index.html')


@csrf_exempt
def api_personas_bridge(request):
    """
    Vista puente para despachar /api/personas cuando se utiliza
    el servidor de desarrollo WSGI de Django (python manage.py runserver).
    """
    if request.method == 'GET':
        personas = Persona.objects.all().order_by('-id')
        data = [PersonaOut.model_validate(p).model_dump(mode='json') for p in personas]
        return JsonResponse(data, safe=False, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            payload = PersonaCreate(**body)
        except (json.JSONDecodeError, PydanticValidationError) as e:
            return JsonResponse({'error': str(e)}, status=422)

        persona = Persona(
            nombres_completos=payload.nombres_completos,
            fecha_nacimiento=payload.fecha_nacimiento,
        )
        persona.save()
        return JsonResponse(
            PersonaOut.model_validate(persona).model_dump(mode='json'),
            status=201,
        )

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
