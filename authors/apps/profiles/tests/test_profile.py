from rest_framework import status
from rest_framework.test import APIClient
from . import BaseTest
from authors.apps.profiles.models import Profile


class AuthenticationTests(BaseTest):

    def test_profile_is_with_the_user_instance(self):
        response = self.client.get('/api/profiles/Jacob1/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_a_non_existing_profile(self):
        response = self.client.get('/api/profiles/notfound/', format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_profile_is_successful(self):
        data = {
                "user": {
                    "bio": "Test bio",
                    "image": "https://pixabay.com/en/avatar-person-neutral-man-blank-",
                    "location": " Kampala uganda",
                    "occupation": "Dev at Andela"
                    }
                }
        response = self.client.put('/api/user/', data, format="json")
        self.assertIn("Dev at Andela", response.data['occupation'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_retrieve_their_profile(self):
        response = self.client.get('/api/user/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_retrieve_other_users_profile(self):
        response = self.client.get('/api/profiles/user/Jacob1/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_not_found(self):
        response = self.client.get('/api/profiles/user/not_found/', format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_Unauthenticated_user(self):
        self.user_validate_data = {"user": {"username": "llll",
                                            "email": "l@gmail.com",
                                            "password": "p1234567"
                                            }
                                   }
        self.un_auth_client = APIClient()
        response = self.un_auth_client.get('/api/profiles/user/Jacob1/', format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
