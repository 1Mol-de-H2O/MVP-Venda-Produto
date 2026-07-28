from rest_framework import serializers
from .models import Pedido, ItemPedido

class ItemPedidoSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'titulo_produto', 'preco_unitario', 'quantidade', 'subtotal']

    def get_subtotal(self, obj):
        return obj.preco_unitario * obj.quantidade

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'status', 'total', 'criado_em', 'itens']
        read_only_fields = ['status', 'total', 'criado_em']