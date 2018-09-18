from django.http import JsonResponse

from finance.forms import OfferForm
from finance.models import Offer, Issue


def offers(request, issue_id):
    issue = Issue.objects.find(pk=issue_id)
    if request.method == 'GET':
        possible_offers = Offer.objects.filter(
            min_loan_size__lt=issue.amount,
            max_loan_size__gt=issue.amount,
            return_period__lt=issue.max_credit_period
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
