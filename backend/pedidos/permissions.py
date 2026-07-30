from rest_framework import permissios

class IsDonoDoPedido(permissios.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.cliente == request.user