from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class CanUpdateInventory(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = request.user.is_authenticated and request.user.can_update_inventory
        logger.info(f"CanUpdateInventory permission check for user {request.user}: {has_permission}")
        return has_permission