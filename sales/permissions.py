from rest_framework import permissions

class CanReportSales(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_report_sales