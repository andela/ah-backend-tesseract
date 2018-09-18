import logging
from rest_framework.exceptions import ValidationError

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


from authors.apps.notifications.models import Notification, Subscription, Recipient
from authors.apps.notifications.serializers import NotificationSerializer, SubscriptionSerializer


class NotificationsAPIView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = NotificationSerializer

    def get(self, request):

        # Fetch the notifications if user is subscribed to get them by app
        # get only notifications that concern a user in request ????
        # we get notifications about an article in users favorites
        # and about new articles created by authors a user is following

        recipients = Recipient.objects.filter(user=request.user)

        if not recipients:
            raise ValidationError("You do not have notifications")
        notifications = [recipient.notification for recipient in recipients]
        serializer = self.serializer_class(notifications, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionAPIView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = SubscriptionSerializer

    def put(self, request, channel, subscribe):
        request.data[channel] = subscribe
        serializer = self.serializer_class(data=request.data)
        try:
            instance = Subscription.objects.get(user=request.user)
            serializer.update(instance, request.data)
        except Subscription.DoesNotExist:
            logging.error(" User not Subscription table")

        return Response({"message": "Action was successful"}, status=status.HTTP_200_OK)
