from finance import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'offers', views.OffersViewSet)
router.register(r'issues', views.IssueViewSet)
router.register(r'debts', views.DebtViewSet)
router.register(r'match', views.MatchViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
