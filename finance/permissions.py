from rest_framework import permissions


class IsAdminOrPostOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method == 'POST':
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return request.user.is_staff


class IsCreditor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_creditor


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.borrower or request.user == obj.creditor

