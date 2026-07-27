from django.db import models
from django.conf import settings
from produtos.models import Produto

class Carrinho(models.Model):
    cliente = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrinho')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Carrinho de {self.cliente.username}'

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrinho', 'produto')

    def __str__(self):
        return f'{self.quantidade}x {self.produto.titulo}'