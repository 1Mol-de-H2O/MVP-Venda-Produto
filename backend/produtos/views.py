from rest_framework import viewsets, filters
from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer
from .permissions import IsVendedorOuSomenteLeitura

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'categoria__nome']
    permission_classes = [IsVendedorOuSomenteLeitura]

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)