from django.db import models
from django.conf import settings
from produtos.models import Produto

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    METODO_PAGAMENTO_CHOICES =[
        ('cartao', 'Cartao'),
        ('boleto', 'Boleto'), 
        ('pix', 'Pix'),
    ]

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cupom_codigo = models.CharField(max_length=20, blank=True, null=True)

    endereco_cep = models.CharField(max_length=9)
    endereco_rua = models.CharField(max_length=255)
    endereco_numero = models.CharField(max_length=20)
    endereco_complemento = models.CharField(max_length=100, blank=True)
    endereco_bairro = models.CharField(max_length=100)
    endereco_cidade = models.CharField(max_length=100)
    endereco_estado = models.CharField(max_length=2)

    metodo_pagamento = models.CharField(max_length=10, choices=METODO_PAGAMENTO_CHOICES, default='cartao')

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.username}'

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    titulo_produto = models.CharField(max_length=255)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantidade}x {self.titulo_produto}'