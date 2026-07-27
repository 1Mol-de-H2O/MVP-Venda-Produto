from django.urls import path
from .views import ver_carrinho, adicionar_item, remover_item

urlpatterns = [
    path('carrinho/', ver_carrinho, name='ver-carrinho'),
    path('carrinho/adicionar/', adicionar_item, name='adicionar-item'),
    path('carrinho/remover/<int:item_id>/', remover_item, name='remover-item')
]