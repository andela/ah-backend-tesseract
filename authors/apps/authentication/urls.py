from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ActivateAccountAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('activate/<str:user_id>/<str:token>/account/', ActivateAccountAPIView.as_view(), name='activate'),
    path('users/login/', LoginAPIView.as_view()),
]
