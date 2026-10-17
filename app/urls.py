from django.urls import path
from .views import IndexView, PersonaApiBridgeView

app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('api/personas', PersonaApiBridgeView.as_view(), name='api_personas_bridge'),
    path('api/personas/', PersonaApiBridgeView.as_view(), name='api_personas_bridge_slash'),
]
