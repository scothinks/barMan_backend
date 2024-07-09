from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class BasePermission(permissions.BasePermission):
    permission_name = ""

    def has_permission(self, request, view):
        logger.info(f"Checking {self.permission_name} permission for user: {request.user}")
        has_perm = request.user.is_authenticated and getattr(request.user, self.permission_name, False)
        logger.info(f"User has {self.permission_name} permission: {has_perm}")
        return has_perm

class CanUpdateInventory(BasePermission):
    permission_name = "can_update_inventory"

class CanReportSales(BasePermission):
    permission_name = "can_report_sales"

class CanCreateCustomers(BasePermission):
    permission_name = "can_create_customers"

class CanCreateTabs(BasePermission):
    permission_name = "can_create_tabs"

class CanUpdateTabs(BasePermission):
    permission_name = "can_update_tabs"

class CanManageUsers(BasePermission):
    permission_name = "can_manage_users"