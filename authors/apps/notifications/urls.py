from django.urls import path

from .views import (NotificationsAPIView, SubscriptionAPIView)

urlpatterns = [
    path('notifications/', NotificationsAPIView.as_view()),
    path('notifications/<str:channel>/<str:subscribe>',
         SubscriptionAPIView.as_view(), name='subscribe_unsubscribe'),
]
