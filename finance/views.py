from django.http import JsonResponse
from django.core.paginator import Paginator

from idebt.ajax import ajax

from finance.forms import OfferForm, IssueForm, MatchForm
from finance.models import Offer, Issue


PER_PAGE = 10


@ajax(login_required=True, require_GET=True)
def get_offers_for_issue(request, issue_id):
    issue = Issue.objects.get(pk=issue_id)
    offers = issue.get_offers()
    page = request.GET.get('page')
    return JsonResponse([
        offer.to_json()
        for offer in Paginator(offers, PER_PAGE).get_page(page)
    ], safe=False)


@ajax(login_required=True, require_GET=True, require_POST=True)
def create_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({
                "status": "error",
                "error": form.errors
            }, status=422)
    elif request.user.is_creditor:
        page = request.GET.get('page')
        return JsonResponse([
            credit.to_json()
            for credit in Paginator(request.user.credits, PER_PAGE).get_page(page)
        ], safe=False)
    else:
        return JsonResponse({
            "status": "error",
            "error": "Only creditor users allow to list their credits"
        }, status=403)


@ajax(login_required=True, require_GET=True)
def get_issues_for_offer(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    issues = offer.get_issues()
    page = request.GET.get('page')
    return JsonResponse([
        issue.to_json()
        for issue in Paginator(issues, PER_PAGE).get_page(page)
    ], safe=False)


@ajax(login_required=True, require_POST=True)
def create_issue(request):
    form = IssueForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({
            "status": "error",
            "message": form.errors
        }, status=422)


@ajax(login_required=True, require_POST=True)
def create_match(request):
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
    else:
        return JsonResponse({
            "status": "error",
            "error": form.errors
        }, status=422)


@ajax(login_required=True, require_GET=True)
def get_debts_for_user(request):
    page = request.GET.get('page')
    return JsonResponse([
        debt.to_json()
        for debt in Paginator(request.user.debts, PER_PAGE).get_page(page)
    ], safe=False)
