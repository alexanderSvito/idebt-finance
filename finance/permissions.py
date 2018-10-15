from rest_framework import permissions


class IsAdminOrPostOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method == 'POST':
            return True

        return request.user.is_staff or request.user.is_superuser


class IsCreditor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_creditor


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.borrower or request.user == obj.creditor


class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return request.user == obj.owner
        return request.user == obj


class IsBorrower(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.borrower