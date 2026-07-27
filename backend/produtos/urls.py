from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, CategoriaViewSet

router = DefaultRouter()
router.register('produtos', ProdutoViewSet)
router.register('categorias', CategoriaViewSet)

urlpatterns = router.urls