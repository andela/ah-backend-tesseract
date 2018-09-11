from rest_framework import status
from authors.apps.authentication.tests import BaseTest


class SocialAuthenticationTests(BaseTest):

    def test_google_invalid_login(self):
        response = self.client.post("/api/social/", self.google_invalid_login, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_provider_login(self):
        response = self.client.post("/api/social/", self.invalid_provider, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_facebook_login(self):
        response = self.client.post("/api/social/", self.facebook_login, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_facebook_invalid_login(self):
        response = self.client.post("/api/social/", self.facebook_invalid_login, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
