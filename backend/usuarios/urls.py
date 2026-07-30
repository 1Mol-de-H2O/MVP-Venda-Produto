from django.urls import path
from .views import meu_perfil, tornar_vendedor, registrar

urlpatterns = [
    path('usuarios/registrar/', registrar, name='registrar'),
    path('usuarios/me/', meu_perfil, name='meu-perfil'),
    path('usuarios/tornar-vendedor/', tornar_vendedor, name='tornar-vendedor'),
]