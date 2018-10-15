from users import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'user', views.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
