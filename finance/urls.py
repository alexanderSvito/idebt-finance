from finance import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'offers', views.OffersViewSet, base_name='offers')
router.register(r'issues', views.IssueViewSet, base_name='issues')
router.register(r'debts', views.DebtViewSet, base_name='debts')
router.register(r'match', views.MatchViewSet, base_name='match')


urlpatterns = [
    url(r'^', include(router.urls))
]
