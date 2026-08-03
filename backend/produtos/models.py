from django.db import models
from django.conf import settings

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    titulo = models.CharField(max_length=250)
    marca = models.CharField(max_length=100, blank=True)
    categoria = models.ManyToManyField(Categoria, related_name='produtos')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='produtos')
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    criado_em = models.DateTimeField(auto_now_add=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    def __str__(self):
        return self.titulo
