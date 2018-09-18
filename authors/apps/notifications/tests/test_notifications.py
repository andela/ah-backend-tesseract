from django.test import override_settings
from rest_framework import status

from authors.apps.notifications.tasks import send_email_notifications
from authors.apps.notifications.tests import BaseTest


class NotificationTests(BaseTest):

    def test_get_user_notifications(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.user3_token)
        response = self.client.get("/api/notifications/",  format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_notifications_empty(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.user1_token)
        response = self.client.get("/api/notifications/",  format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_unsubscribes(self):
        self.assertEqual(self.unsubscribe_app.status_code, status.HTTP_200_OK)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_send_emails(self):
        # This function does not return anything, its a background job
        self.assertIsNone(send_email_notifications())

