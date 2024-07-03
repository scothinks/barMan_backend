from rest_framework import permissions

class CanUpdateInventory(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_update_inventory