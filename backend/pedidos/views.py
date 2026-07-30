from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from carrinho.models import Carrinho
from cupons.models import Cupom
from .models import Pedido, ItemPedido
from .serializers import PedidoSerializer, FinalizarPedidoSerializer
from .frete import calcular_frete

# from django.shortcuts import render

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalizar_pedido(request):
    dados_serializer = FinalizarPedidoSerializer(data=request.data)
    if not dados_serializer.is_valid():
        return Response(dados_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    dados = dados_serializer.validated_data

    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
    except Carrinho.DoesNotExist:
        return Response({'detail': 'Carrinho vazio.'}, status=status.HTTP_400_BAD_REQUEST)

    itens_carrinho = carrinho.itens.all()
    if not itens_carrinho.exists():
        return Response({'detail': 'Carrinho vazio.'}, status=status.HTTP_400_BAD_REQUEST)

    for item in itens_carrinho:
        if item.quantidade > item.produto.estoque:
            return Response(
                {'detail': f'Estoque insuficiente para "{item.produto.titulo}". Disponível: {item.produto.estoque}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    with transaction.atomic():
        subtotal = 0
        peso_total = 0
        for item in itens_carrinho:
            subtotal = subtotal + (item.produto.preco * item.quantidade)
            peso_total = peso_total + (item.produto.peso_kg * item.quantidade)

        frete = calcular_frete(peso_total, valor_compra=subtotal)

        desconto = 0
        cupom_codigo = dados.get('cupom_codigo', '').strip()
        if cupom_codigo:
            try:
                cupom = Cupom.objects.get(codigo__iexact=cupom_codigo)
            except Cupom.DoesNotExist:
                return Response({'detail': 'Cupom não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

            valido, motivo = cupom.esta_valido(valor_compra=subtotal)
            if not valido:
                return Response({'detail': f'Cupom inválido: {motivo}'}, status=status.HTTP_400_BAD_REQUEST)

            desconto = cupom.calcular_desconto(subtotal)
            cupom.usos_atuais += 1
            cupom.save()

        total = subtotal + frete - desconto

        pedido = Pedido.objects.create(
            cliente=request.user,
            subtotal=subtotal,
            frete=frete,
            desconto=desconto,
            total=total,
            cupom_codigo=cupom_codigo or None,
            status='pendente',
            endereco_cep=dados['endereco_cep'],
            endereco_rua=dados['endereco_rua'],
            endereco_numero=dados['endereco_numero'],
            endereco_complemento=dados.get('endereco_complemento', ''),
            endereco_bairro=dados['endereco_bairro'],
            endereco_cidade=dados['endereco_cidade'],
            endereco_estado=dados['endereco_estado'],
            metodo_pagamento=dados['metodo_pagamento'],
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
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')
    serializer = PedidoSerializer(pedidos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, cliente=request.user)
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
        peso_total = peso_total + (item.produto.peso_kg * item.quantidade)
        subtotal = subtotal + (item.produto.preco * item.quantidade)

    frete = calcular_frete(peso_total, valor_compra=subtotal)

    return Response({
        'peso_total_kg': float(peso_total),
        'subtotal': float(subtotal),
        'frete': float(frete),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_vendas(request):
    if not request.user.is_vendedor:
        return Response({'detail': 'Apenas vendedores podem acessar'}, 
                         status=status.HTTP_403_FORBIDEN)

    itens_vendidos = ItemPedido.objects.filter(produto__vendedor=request.user
    ).select_related('pedido', 'pedido__cliente', 'produto').order_by('-pedido__criado_em')

    status_filtro = request.query_params.get('status')
    if status_filtro:
        itens_vendidos = itens_vendidos.filter(pedido__status=status_filtro)

    resultado = []
    for item in itens_vendidos:
        resultado.append({
            'pedido_id': item.pedido.id,
            'cliente': item.pedido.cliente.username,
            'cliente_email': item.pedido.cliente.email,
            'produto': item.titulo_produto,
            'quantidade': item.quantidade,
            'preco_unitario': float(item.preco_unitario),
            'subtotal': float(item.preco_unitario * item.quantidade),
            'status_pedido': item.pedido.status,
            'data': item.pedido.criado_em,
        })

    return Response(resultado)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def atualizar_status_pedido(request, pedido_id):
    if not request.user.is_vendedor:
        return Response({'detail': 'Apenas vendedores podem atualizar status de pedidos.'}, status=status.HTTP_403_FORBIDDEN)

    item = ItemPedido.objects.filter(
        pedido_id=pedido_id, produto__vendedor=request.user
    ).select_related('pedido').first()

    if not item:
        return Response({'detail': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    novo_status = request.data.get('status')
    if novo_status not in dict(Pedido.STATUS_CHOICES):
        return Response({'detail': 'Status inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    pedido = item.pedido
    pedido.status = novo_status
    pedido.save()

    serializer = PedidoSerializer(pedido)
    return Response(serializer.data)