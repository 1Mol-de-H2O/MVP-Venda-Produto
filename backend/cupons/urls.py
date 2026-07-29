from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CupomViewSet, validar_cupom

router = DefaultRouter()
router.register('cupons', CupomViewSet)

urlpatterns = [
    path('cupons/validar/', validar_cupom, name = 'validar-cupom'),
] + router.urls