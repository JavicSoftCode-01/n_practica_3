import json
from django.http import HttpResponseNotAllowed, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from pydantic import ValidationError as PydanticValidationError

from app.models import Persona
from app.schemas import PersonaCreate, PersonaOut


class IndexView(TemplateView):
    """
    Vista basada en clases (CBV) para el portal corporativo.
    Renderiza la interfaz principal (40% formulario y 50% tabla, con base académica 20% y 70%).
    """
    template_name = 'app/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class PersonaApiBridgeView(View):
    """
    Controlador basado en clases (CBV) para el despacho de peticiones RESTful a /api/personas.
    Aplica serialización y deserialización estricta con Pydantic garantizando compatibilidad
    total entre el servidor Django clásico (WSGI) y el servidor FastAPI (ASGI).
    """
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        """
        Serializa y retorna la lista completa de registros ordenados descendentemente por ID.
        """
        personas = Persona.objects.all().order_by('-id')
        data = [PersonaOut.model_validate(p).model_dump(mode='json') for p in personas]
        return JsonResponse(data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        """
        Valida el payload entrante con PersonaCreate y persiste el registro en PostgreSQL.
        """
        try:
            body = json.loads(request.body.decode('utf-8'))
            payload = PersonaCreate(**body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'El formato de los datos enviados no es un JSON válido.'},
                status=400
            )
        except PydanticValidationError as e:
            mensajes = []
            for err in e.errors():
                m = err.get('msg', '')
                if m.startswith('Value error, '):
                    m = m.replace('Value error, ', '')
                mensajes.append(m)
            return JsonResponse({'error': '; '.join(mensajes), 'detail': e.errors()}, status=422)

        persona = Persona(
            nombres_completos=payload.nombres_completos,
            fecha_nacimiento=payload.fecha_nacimiento,
        )
        persona.save()
        return JsonResponse(
            PersonaOut.model_validate(persona).model_dump(mode='json'),
            status=201,
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['GET', 'POST'])


# Aliases para compatibilidad con llamadas directas
index = IndexView.as_view()
api_personas_bridge = PersonaApiBridgeView.as_view()
