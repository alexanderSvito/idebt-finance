from django.http import JsonResponse

from finance.forms import OfferForm, IssueForm, MatchForm
from finance.models import Offer, Issue, Match, Debt


def get_offers_for_issue(request, issue_id):
    issue = Issue.objects.find(pk=issue_id)
    if request.method == 'GET':
        possible_offers = Offer.objects.filter(
            min_loan_size__le=issue.amount,
            max_loan_size__ge=issue.amount,
            return_period__le=issue.max_credit_period
        )
        return JsonResponse([
            offer.to_json()
            for offer in possible_offers
            if offer.overpay_for(issue.amount) <= issue.max_overpay
        ])


def create_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})


def get_issues_for_offer(request, offer_id):
    offer = Offer.objects.find(pk=offer_id)
    if request.method == 'GET':
        possible_issues = Issue.objects.filter(
            amount__le=offer.max_loan_size,
            amount__ge=offer.min_loan_size,
            max_credit_period__ge=offer.return_period
        )
        return JsonResponse([
            issue.to_json()
            for issue in possible_issues
            if offer.overpay_for(issue.amount) <= issue.max_overpay
        ])


def create_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})


def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            if form.cleaned_data['match_type'] == 'OFF':
                offer_id = form.cleaned_data['from_id']
                issue_id = form.cleaned_data['to_id']
            else:
                offer_id = form.cleaned_data['to_id']
                issue_id = form.cleaned_data['from_id']
            if Match.is_matched(offer_id, issue_id):
                debt = Debt.create_from(offer_id, issue_id)
                return JsonResponse({
                    "status": "matched",
                    "debt": debt.to_json()
                    })
            else:
                return JsonResponse({
                    "status": "ok",
                })
