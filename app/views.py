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
    template_name = 'app/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class PersonaApiBridgeView(View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        personas = Persona.objects.all().order_by('-id')
        data = [PersonaOut.model_validate(p).model_dump(mode='json') for p in personas]
        return JsonResponse(data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
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


index = IndexView.as_view()
api_personas_bridge = PersonaApiBridgeView.as_view()
