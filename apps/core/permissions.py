from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

class IsSupplierUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'supplier'

class IsSupplierOfGrocery(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type != 'supplier':
            return False
        
        # Check if supplier is assigned to this grocery
        try:
            supplier_profile = request.user.supplier_profile
            return supplier_profile.assigned_grocery == obj.grocery
        except:
            return False

class CanModifyGroceryItems(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'admin':
            return True
        
        if request.user.user_type == 'supplier':
            try:
                supplier_profile = request.user.supplier_profile
                return supplier_profile.assigned_grocery == obj.grocery
            except:
                return False
        
        return False


class IsGroceryOwner(permissions.BasePermission):
    """Check if user created the grocery"""
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user