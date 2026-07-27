from rest_framework.decorators import api_view, permission_classes
from rest_framework.permission import IsAutheticated
from rest_framework.response import Response
from rest_framework import status
from .models import Carrinho, ItemCarrinho
from .serializers import CarrinhoSerializer
from produtos.models import Produto

from django.shortcuts import render

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAutheticated])
def ver_carrinho(request):
    carrinho, _ = Carrinho.objects.get_or_create(cliente=request.user)
    serializer = CarrinhoSerializer(carrinho)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAutheticated])
def adicionar_item(request):
    carrinho, _ = Carrinho.objects.get_or_create(cliente=request.user)
    produto_id = request.data.get('produto')
    quantidade = int(request.data.get('quantidade', 1))

    try:
        produto = Produto.objects.get(id=produto_id)
    except Produto.DoesNotExist:
        return Response({'detail': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    item, criado = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)
    if criado:
        item.quantidade = quantidade
    else:
        item.quantidade += quantidade
    item.save()

    serializer = CarrinhoSerializer(carrinho)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAutheticated])
def remover_item(request, item_id):
    try:
        item = ItemCarrinho.objects.get(id=item_id, carrinho__cliente=request.user)
    except ItemCarrinho.DoesNotExist:
        return Response({'detail': 'Item não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    item.delete()
    carrinho = Carrinho.objects.get(cliente=request.user)
    serializer = CarrinhoSerializer(carrinho)
    return Response(serializer.data)