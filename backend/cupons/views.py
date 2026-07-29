from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cupom
from .serializers import CupomSerializer
from produtos.permissions import IsVendedorOuSomenteLeitura
from decimal import Decimal, InvalidOperation

# from django.shortcuts import render

# Create your views here.


class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer
    permission_classes = [IsVendedorOuSomenteLeitura]

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validar_cupom(request):
    codigo = request.data.get('codigo')
    valor_compra = request.data.get('valor_compra')

    if not codigo:
        return Response({'detail': 'O código do cupom é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

    valor_compra_raw = request.data.get('valor_compra')

    valor_compra = None
    if valor_compra_raw is not None:
        try:
            valor_compra = Decimal(str(valor_compra_raw))
            if valor_compra < 0:
                return Response({'detail': 'O valor da compra não pode ser negativo'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, InvalidOperation):
            return Response({'detail': 'Valor de compra inválido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cupom = Cupom.objects.get(codigo__iexact=codigo.strip())
    except Cupom.DoesNotExist:
        return Response({'detail': 'Cupom não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    valido, motivo = cupom.esta_valido(valor_compra=valor_compra)
    if not valido:
        return Response({'detail': motivo}, status=status.HTTP_400_BAD_REQUEST)

    desconto = Decimal('0.00')
    valor_final = None

    if valor_compra is not None:
        desconto = cupom.calcular_desconto(valor_compra)
        valor_final_decimal = valor_compra - desconto
        desconto_float = float(desconto)
        valor_final = float(valor_final_decimal)
    else:
        desconto_float = 0.0

    return Response(
        {
            'valido': True,
            'mensagem': 'Cupom válido',
            'cupom' : {
                'codigo' : cupom.codigo,
                'tipo' : cupom.tipo,
                'desconto' : desconto_float,
                'valor_final' : valor_final
            }
        }, status=status.HTTP_200_OK
    )