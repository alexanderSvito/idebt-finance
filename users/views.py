from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from finance.exceptions import TransferError
from finance.permissions import IsSelf
from users.models import User
from users.serializers import ShallowUserSerializer, UserSerializer, PasswordSerializer

from rest_framework_jwt.settings import api_settings


BLACKLIST_FIELDS = {
    "password",
}


class UserViewSet(viewsets.ReadOnlyModelViewSet, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_shallow_user_info(self, user):
        return {
            k: v
            for k, v in user.data.items()
            if k not in BLACKLIST_FIELDS
        }

    def list(self, request, **kwargs):
        users = self.get_queryset()

        page = self.paginate_queryset(users)

        if not request.user.is_staff and not request.user.is_superuser:
            serializer = ShallowUserSerializer(page, many=True)
        else:
            serializer = self.get_serializer(page, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_staff and not request.user.is_superuser:
            serializer = ShallowUserSerializer(user)
        else:
            serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def me(self, request, **kwargs):
        user = request.user
        user.password = '<hidden>'
        serializer = self.get_serializer(instance=user)
        return Response(self._get_shallow_user_info(serializer))

    @action(methods=['post'], detail=True, permission_classes=[IsSelf])
    def set_password(self, request, pk=None, **kwargs):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.save())
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True, url_path='balance/replenish',
            permission_classes=[IsSelf])
    def replenish(self, request, pk=None, **kwargs):
        user = self.get_object()
        try:
            user.replenish(request.data['amount'])
            return Response({'status': 'balance updated'})
        except Exception as e:
            return Response(str(e),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True, url_path='balance/withdraw',
            permission_classes=[IsSelf])
    def withdraw(self, request, pk=None, **kwargs):
        user = self.get_object()
        try:
            user.withdraw(request.data['amount'])
            return Response({'status': 'balance updated'})
        except TransferError as e:
            return Response(str(e),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, permission_classes=[permissions.AllowAny])
    def signup(self, request, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = PasswordSerializer(data=request.data)
            if password.is_valid():
                user = serializer.save()
                password = password.save()
                user.password = password
                user.save()
                payload = api_settings.JWT_PAYLOAD_HANDLER(user)
                response_data = {
                    "user": self._get_shallow_user_info(serializer),
                    "token": api_settings.JWT_ENCODE_HANDLER(payload)
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
