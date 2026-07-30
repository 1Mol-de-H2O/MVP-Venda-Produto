from django.urls import path
from .views import finalizar_pedido, meus_pedidos, detalhe_pedido, calcular_frete_carrinho

urlpatterns = [
    path('pedidos/finalizar/', finalizar_pedido, name='finalizar-pedido'),
    path('pedidos/meus/', meus_pedidos, name='meus-pedidos'),
    path('pedidos/frete/', calcular_frete_carrinho, name='calcular-frete'),
    path('pedidos/<int:pedido_id>/', detalhe_pedido, name='detalhe-pedido'),
]