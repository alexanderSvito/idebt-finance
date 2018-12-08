from stats import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'stats', views.StatsViewSet, base_name='stats')


urlpatterns = [
    url(r'^', include(router.urls))
]
