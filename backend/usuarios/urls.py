from django.urls import path
from .views import meu_perfil, tornar_vendedor

urlpatterns = [
    path('usuarios/me/', meu_perfil, name='meu-perfil'),
    path('usuarios/tornar-vendedor/', tornar_vendedor, name='tornar-vendedor'),
]