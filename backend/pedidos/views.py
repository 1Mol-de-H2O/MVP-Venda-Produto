from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from carrinho.models import Carrinho
from .models import Pedido, ItemPedido
from .serializers import PedidoSerializer
from .frete import calcular_frete

# from django.shortcuts import render

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalizar_pedido(request):
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
    except Carrinho.DoesNotExist:
        return Response({'detail': 'Carrinho vazio.'}, status=status.HTTP_400_BAD_REQUEST)

    itens_carrinho = carrinho.itens.all()
    if not itens_carrinho.exists():
        return Response({'detail': 'Carrinho vazio.'}, status=status.HTTP_400_BAD_REQUEST)

    for item in itens_carrinho:
        if item.quantidade > item.produto.estoque:
            return Response (
                {'detail': f'Estoque insuficiente para "{item.produto.titulo}". Disponível: {item.produto.estoque}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    with transaction.atomic():
        subtotal = 0
        peso_total = 0
        for item in itens_carrinho:
            preco_do_produto = item.produto.preco
            quantidade_comprada = item.quantidade
            subtotal_do_item = preco_do_produto * quantidade_comprada
            subtotal = subtotal + subtotal_do_item
            peso_total = peso_total + (item.produto.peso_kg * quantidade_comprada)

        frete = calcular_frete(peso_total, valor_compra=subtotal)
        total = subtotal + frete

        pedido = Pedido.objects.create(
            cliente=request.user,
            total=total,
            frete=frete,
            status='pendente'
        )

        for item in itens_carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                titulo_produto=item.produto.titulo,
                preco_unitario=item.produto.preco,
                quantidade=item.quantidade,
            )
            item.produto.estoque -= item.quantidade
            item.produto.save()

        itens_carrinho.delete()

    serializer = PedidoSerializer(pedido)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(cliente = request.user).order_by('-criado_em')
    serializer = PedidoSerializer(pedidos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, cliente = request.user)
    except Pedido.DoesNotExist:
        return Response({'detail': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PedidoSerializer(pedido)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calcular_frete_carrinho(request):
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
    except Carrinho.DoesNotExist:
        return Response({'detail': 'Carrinho vazio'}, status=status.HTTP_400_BAD_REQUEST)

    itens = carrinho.itens.all()
    if not itens.exists():
        return Response({'detail': 'Carrinho vazio'}, status=status.HTTP_400_BAD_REQUEST)

    peso_total = 0
    subtotal = 0
    for item in itens:
        peso_do_produto = item.produto.peso_kg
        quantidade_comprada = item.quantidade
        peso_do_item = peso_do_produto * quantidade_comprada
        peso_total = peso_total + peso_do_item
        subtotal = subtotal + (item.produto.preco * quantidade_comprada)

    frete = calcular_frete(peso_total, valor_compra=subtotal)

    return Response({'peso_total_kg': float(peso_total), 'frete': float(frete),})