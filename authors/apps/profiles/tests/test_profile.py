from rest_framework import status
from rest_framework.test import APIClient
from . import BaseTest


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

        self.un_auth_client = APIClient()
        response = self.un_auth_client.get('/api/profiles/user/Jacob1/', format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_can_not_follow_them_selves(self):
        response = self.client.post('/api/profiles/user_test/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You can not follow yourself.', str(response.data))

    def test_unfollow_user(self):
        self.client.post('/api/profiles/Jacob1/follow', format="json")
        response = self.client.delete('/api/profiles/Jacob1/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_Unauthenticated_user_attempts_to_follow(self):
        self.un_auth_client = APIClient()
        response = self.un_auth_client.get('/api/profiles/Jacob1/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_can_follow_each_other(self):
        response = self.client.post('/api/profiles/Jacob1/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Jacob1', str(response.data))

    def test_follow_an_invalid_profile(self):
        response = self.client.post('/api/profiles/ivalid_username/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_an_invalid_profile(self):
        response = self.client.delete('/api/profiles/ivalid_username/follow', format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fetching_list_of_user_profiles(self):
        response = self.client.get('/api/profiles/users', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "users")