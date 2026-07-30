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
        fields = [
            'id', 'status', 'subtotal', 'desconto', 'frete', 'total', 'cupom_codigo',
            'endereco_cep', 'endereco_rua', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cidade', 'endereco_estado',
            'metodo_pagamento', 'criado_em', 'itens',
        ]
        read_only_fields = ['status', 'subtotal', 'desconto', 'frete', 'total', 'cupom_codigo', 'criado_em']

class FinalizarPedidoSerializer(serializers.Serializer):
    endereco_cep = serializers.CharField(max_length=9)
    endereco_rua = serializers.CharField(max_length=255)
    endereco_numero = serializers.CharField(max_length=20)
    endereco_complemento = serializers.CharField(max_length=100, required=False, allow_blank=True)
    endereco_bairro = serializers.CharField(max_length=100)
    endereco_cidade = serializers.CharField(max_length=100)
    endereco_estado = serializers.CharField(max_length=2)
    metodo_pagamento = serializers.ChoiceField(choices=Pedido.METODO_PAGAMENTO_CHOICES)
    cupom_codigo = serializers.CharField(max_length=20, required=False, allow_blank=True)