from rest_framework import viewsets, permissions, status

from finance.exceptions import TransferError
from finance.permissions import IsCreditor, IsAdminOrPostOnly, IsOwner, IsSelf, IsBorrower
from finance.serializers import OfferSerializer, IssueSerializer, MatchSerializer, DebtSerializer

from finance.models import Offer, Issue, Match, Debt
from rest_framework.decorators import action
from rest_framework.response import Response


class OffersViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreditor)

    def list(self, request, *args, **kwargs):
        offers = self.get_queryset()

        if not request.user.is_superuser and not request.user.is_staff:
            offers = offers.filter(creditor=request.user)

        page = self.paginate_queryset(offers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

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

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["creditor"] = request.user.id
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


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def list(self, request, *args, **kwargs):
        issues = self.get_queryset()

        if not request.user.is_superuser and not request.user.is_staff:
            issues = issues.filter(borrower=request.user)

        page = self.paginate_queryset(issues)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(issues, many=True)
        return Response(serializer.data)

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

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["borrower"] = request.user.id
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


class DebtViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def list(self, request, *args, **kwargs):
        debts = self.get_queryset()

        if not request.user.is_superuser and not request.user.is_staff:
            debts = debts.filter(borrower=request.user)

        page = self.paginate_queryset(debts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def i_owe(self, request):
        debts = Debt.objects.filter(borrower=request.user)

        page = self.paginate_queryset(debts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def owe_me(self, request):
        debts = Debt.objects.filter(creditor=request.user)

        page = self.paginate_queryset(debts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=True, permission_classes=[IsBorrower])
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
    permission_classes = (permissions.IsAuthenticated, IsAdminOrPostOnly)

    def create(self, request):
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

