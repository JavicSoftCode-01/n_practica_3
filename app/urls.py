from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/personas', views.api_personas_bridge, name='api_personas_bridge'),
    path('api/personas/', views.api_personas_bridge, name='api_personas_bridge_slash'),
]
