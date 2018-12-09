from wsgiref.util import FileWrapper

from django.http import HttpResponse
from rest_framework import viewsets, permissions, status

from finance.exceptions import TransferError, CloseError
from finance.permissions import IsCreditor, IsAdminOrPostOnly, IsOwner, IsBorrower, IsMatchable
from finance.serializers import OfferSerializer, IssueSerializer, MatchSerializer, DebtSerializer

from finance.models import Offer, Issue, Match, Debt
from rest_framework.decorators import action
from rest_framework.response import Response


class ListMixin(viewsets.ReadOnlyModelViewSet):
    OWNER_NAME = None

    def list(self, request, *args, **kwargs):
        objects = self.get_queryset()

        if not request.user.is_superuser and not request.user.is_staff:
            objects = objects.filter(**{self.OWNER_NAME: request.user})

        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)


class CreateCloseMixin(viewsets.ReadOnlyModelViewSet):
    OWNER_NAME = None

    @action(methods=['post'], detail=True)
    def close(self, request, pk=None):
        obj = self.get_object()
        try:
            obj.close()
            return Response({"status": "ok"})
        except CloseError as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data[self.OWNER_NAME] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except TransferError as e:
                return Response({
                    'status': 'error',
                    'message': e
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class OffersViewSet(ListMixin, CreateCloseMixin):
    OWNER_NAME = 'creditor'

    queryset = Offer.objects.filter(is_closed=False)
    serializer_class = OfferSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreditor, IsOwner)

    @action(detail=True)
    def suitable(self, request, pk=None):
        offer = self.get_object()
        suitable_issues = offer.get_issues()

        page = self.paginate_queryset(suitable_issues)
        if page is not None:
            serializer = IssueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = IssueSerializer(suitable_issues, many=True)
        return Response(serializer.data)


class IssueViewSet(ListMixin, CreateCloseMixin):
    OWNER_NAME = 'borrower'

    queryset = Issue.objects.filter(is_closed=False)
    serializer_class = IssueSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    @action(detail=True, permission_classes=[permissions.IsAuthenticated])
    def suitable(self, request, pk=None):
        issue = self.get_object()
        suitable_offers = issue.get_offers()

        page = self.paginate_queryset(suitable_offers)
        if page is not None:
            serializer = OfferSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OfferSerializer(suitable_offers, many=True)
        return Response(serializer.data)


class DebtViewSet(ListMixin):
    OWNER_NAME = 'borrower'
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    @action(detail=True, permission_classes=[permissions.AllowAny])
    def contract(self, request, pk=None):
        debt = self.get_object()
        pdf_file = open(debt.contract_filename, 'rb')
        response = HttpResponse(FileWrapper(pdf_file), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=contract_{}.pdf'.format(debt.id)
        return response

    @action(detail=False)
    def i_owe(self, request):
        debts = Debt.objects.filter(borrower=request.user, is_closed=False)

        page = self.paginate_queryset(debts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def owe_me(self, request):
        debts = Debt.objects.filter(creditor=request.user, is_closed=False)

        page = self.paginate_queryset(debts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBorrower])
    def repay(self, request, pk=None):
        debt = self.get_object()
        if debt.is_repayable:
            try:
                debt.repay_funds()
                return Response({'status': 'ok'})
            except TransferError as e:
                return Response({
                    'status': 'error',
                    'message': e
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response({
                'status': 'error',
                'message': 'Insufficient funds'
            }, status=status.HTTP_400_BAD_REQUEST)


class MatchViewSet(viewsets.GenericViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrPostOnly,
        IsMatchable
    )

    def create(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                match, is_matched = serializer.save()

                if is_matched:
                    return Response({'status': 'matched'})
                else:
                    return Response({'status': 'ok'})
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        except Offer.DoesNotExist:
            return Response({'detail': 'not found'})
        except Issue.DoesNotExist:
            return Response({'detail': 'not found'})
