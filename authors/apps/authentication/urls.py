from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ActivateAccountAPIView,
    PasswordResetAPIView, ComfirmPasswordResetAPIView, SocialAuthenticationAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('activate/<str:user_id>/<str:token>/account/', ActivateAccountAPIView.as_view(), name='activate'),
    path('users/login/', LoginAPIView.as_view()),
    path('password-reset/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('password-reset/<str:token>/', ComfirmPasswordResetAPIView.as_view(),
         name='comfirm_password_reset'),
    path('password-reset/done', ComfirmPasswordResetAPIView.as_view(), name='password_reset_done'),
    path('social/', SocialAuthenticationAPIView.as_view(), name="social"),

]
