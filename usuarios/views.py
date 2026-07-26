from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UsuarioSerializer

#from django.shortcuts import render

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def meu_perfil(request):
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def tornar_vendedor(request):
    usuario = request.user
    usuario.is_vendedor = True
    usuario.save()
    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data)