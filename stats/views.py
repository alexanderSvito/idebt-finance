from rest_framework import viewsets, permissions
from rest_framework.response import Response

from users.models import User


class StatsViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        response_data = user.get_all_stats()
        return Response(response_data)
