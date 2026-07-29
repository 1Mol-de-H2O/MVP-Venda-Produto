from django.urls import path
from .views import finalizar_pedido, meus_pedidos, detalhe_pedido

urlpatterns = [
    path('pedidos/finalizar/', finalizar_pedido, name = 'detalhe-pedido'),
    path('pedidos/meus/', meus_pedidos, name = 'meus-pedidos'),
    path('pedidos/<int:pedido_id>/', detalhe_pedido, name = 'detalhe-pedido'),
]