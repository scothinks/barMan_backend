from rest_framework import permissions

class CanCreateTabs(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_create_tabs

class CanUpdateTabs(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_update_tabs