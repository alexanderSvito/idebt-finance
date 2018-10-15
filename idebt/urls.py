from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    path('api/', include([
        path('v1/', include([
                path(r'', include('finance.urls')),
                path(r'user/login/', obtain_jwt_token),
                path(r'', include('users.urls')),
                ])
            )
        ]),
    )
]

