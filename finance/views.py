from django.http import JsonResponse

from finance.forms import OfferForm, IssueForm, MatchForm
from finance.models import Offer, Issue, Match, Debt


def get_offers_for_issue(request, issue_id):
    issue = Issue.objects.get(pk=issue_id)
    if request.method == 'GET':
        return JsonResponse([
            offer.to_json()
            for offer in issue.get_offers()
        ])


def create_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})


def get_issues_for_offer(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    if request.method == 'GET':
        return JsonResponse([
            issue.to_json()
            for issue in offer.get_issues()
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
            match, matched, debt = form.save()
            if matched:
                return JsonResponse({
                    "status": "matched",
                    "debt": debt.to_json()
                })
            else:
                return JsonResponse({
                    "status": "ok"
                })
