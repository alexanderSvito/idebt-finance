from finance.views import (
    get_offers_for_issue,
    create_offer,
    get_issues_for_offer,
    create_issue
)
from django.urls import path


urlpatterns = [
    path('offers/<int:issue_id>', get_offers_for_issue),
    path('offers/', create_offer),
    path('issues/<int:offer_id>', get_issues_for_offer),
    path('issues/', create_issue),
]
