from rest_framework import serializers
from .models import Carrinho, ItemCarrinho
from produtos.models import Produto

class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto_titulo = serializers.CharField(source='produto.titulo', read_only=True)
    produto_preco = serializers.DecimalField(source='produto.preco', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'produto', 'produto_titulo', 'produto_preco', 'quantidade', 'subtotal']

    def get_subtotal(self, obj):
        return obj.produto.preco * obj.quantidade


class CarrinhoSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrinho
        fields = ['id', 'itens', 'total']

    def get_total(self, obj):
        total = 0
        for item in obj.itens.all():
            subtotal = item.produto.preco * item.quantidade
            total += subtotal
        return total