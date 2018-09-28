from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from users.views import signup
from idebt import views

urlpatterns = [
    path('api/', include([
            path('v1/',
                 include('finance.urls')
                 )
        ])
    ),
    path(r'signup/', signup),
    path(r'login/', obtain_jwt_token),
]

handler404 = views.custom404
handler500 = views.custom500
