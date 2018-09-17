from django.urls import path

from .views import AuthentivatedProfileRetrieveAPIView, ProfileAPIView, FollowersAPIView, UsersListAPIView

urlpatterns = [
    path('profiles/<str:username>/', ProfileAPIView.as_view(), name='user_profile'),
    path('profiles/user/<str:username>/', AuthentivatedProfileRetrieveAPIView.as_view(), name='auth_user_profile'),
    path('profiles/users', UsersListAPIView.as_view()),
    path('profiles/<str:username>/follow', FollowersAPIView.as_view(), name='follow'),
]
