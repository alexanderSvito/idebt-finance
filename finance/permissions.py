from rest_framework import permissions

from finance.models import Issue, Offer, Match


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
        if isinstance(obj, Issue):
            return request.user == obj.borrower
        elif isinstance(obj, Offer):
            return request.user == obj.creditor
        else:
            return False


class IsMatchable(permissions.BasePermission):
    def has_permission(self, request, view):
        data = request.data
        if data['match_type'] == 'ISS':
            try:
                issue = Issue.objects.get(pk=data['from_id'])
                return issue.borrower == request.user
            except Issue.DoesNotExist:
                return False
        elif data['match_type'] == 'OFF':
            try:
                offer = Offer.objects.get(pk=data['from_id'])
                return offer.creditor == request.user
            except Issue.DoesNotExist:
                return False
        else:
            return False


class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return request.user == obj.owner
        return request.user == obj


class IsBorrower(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.borrower
