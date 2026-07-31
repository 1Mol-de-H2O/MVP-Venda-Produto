from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

class Cupom(models.Model):
    TIPO_CHOICES = [
        ('produto', 'Desconto sobre produto'),
        ('frete', 'Desconto sobre frete'),
    ]

    codigo = models.CharField(max_length = 20, unique = True)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'cupons')
    tipo = models.CharField(max_length = 10, choices = TIPO_CHOICES)
    desconto_percentual = models.DecimalField(max_digits = 5, decimal_places = 2)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    valor_minimo = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    limite_usos = models.PositiveIntegerField(null=True, blank=True)
    usos_atuais = models.PositiveIntegerField(default = 0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo

    def esta_valido(self, valor_compra=None):
        agora = timezone.now()

        if not self.ativo:
            return False, 'Cupom inativo'
        if agora < self.data_inicio or agora > self.data_fim:
            return False, 'Cupom fora do período de validade'
        if self.limite_usos is not None and self.usos_atuais >= self.limite_usos:
            return False, 'Cupom atingiu o limite de usos'
        if self.valor_minimo is not None and valor_compra is not None and valor_compra < self.valor_minimo:
            return False, f'Valor mínimo de compra não atingido (mínimo: R$ {self.valor_minimo})'
        return True, None

    def calcular_desconto(self, valor_compra):
        if not valor_compra or valor_compra <= 0:
            return Decimal('0.00')

        desconto = (valor_compra * self.desconto_percentual/Decimal('100'))
        desconto = desconto.quantize(Decimal('0.01'))

        return min(desconto, valor_compra)
    
# Create your models here.
