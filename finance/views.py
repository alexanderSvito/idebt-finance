from rest_framework import viewsets, permissions, status

from finance.permissions import IsCreditor, IsAdminOrPostOnly, IsOwner
from finance.serializers import OfferSerializer, IssueSerializer, MatchSerializer, DebtSerializer

from finance.models import Offer, Issue, Match, Debt
from rest_framework.decorators import action
from rest_framework.response import Response


class OffersViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True, permission_classes=[IsCreditor, permissions.IsAuthenticated])
    def suitable(self, request, pk=None):
        offer = self.get_object()
        suitable_issues = offer.get_issues()

        page = self.paginate_queryset(suitable_issues)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(suitable_issues, many=True)
        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True)
    def suitable(self, request, pk=None):
        issue = self.get_object()
        suitable_offers = issue.get_offers()

        page = self.paginate_queryset(suitable_offers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(suitable_offers, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["borrower"] = request.user.id
        serializer = IssueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class DebtViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def list(self, request, **kwargs):
        show_credits = kwargs.get('credits', False)
        if show_credits:
            return Debt.objects.filter(creditor=request.user)
        else:
            return Debt.objects.filter(borrower=request.user)


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrPostOnly)

    def create(self, request):
        serializer = MatchSerializer(data=request.data)
        if serializer.is_valid():
            match, is_matched = serializer.save()
            if is_matched:
                return Response({'status': 'matched'})
            else:
                return Response({'status': 'ok'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

