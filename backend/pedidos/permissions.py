from rest_framework import permissions

class IsDonoDoPedido(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.cliente == request.user