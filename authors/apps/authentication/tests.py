from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class BaseTest:
    def __init__(self):

        self.user_data = {"user":
                          {"username": "Jacob1", "email": "jake@jakeg.jake", "password": "jakejakeh"}
                      }

        self.login_data_email = {"user":
                                 {"email": "jake@jakeg.jake", "password": "jakejakeh"}
                             }
        self.unregistered_user_data = {"user":
                                 {"email": "jake@hhd.jake", "password": "jakeakeh"}
                             }


class AuthenticationTests(TestCase, BaseTest):

    def setUp(self):
        BaseTest.__init__(self)
        User.objects.create_user("user_test", "mail@me.com", password="1234")
        self.user = User.objects.get(id=1)
        self.client = APIClient()
        self.register_response = self.client.post("/api/users/", self.user_data, format="json")

    def test_username_label(self):
        field_label = self.user._meta.get_field('username').verbose_name
        self.assertEquals(field_label, 'username')

    def test_get_full_name(self):
        self.assertEquals("user_test", self.user.get_full_name)

    def test_get_short_name(self):
        self.assertEquals("user_test", self.user.get_short_name())

    def test_user_registration(self):

        self.assertEqual(self.register_response.status_code, status.HTTP_201_CREATED)

    def test_user_login_with_email(self):
        response = self.client.post("/api/users/login/", self.login_data_email, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_invalid_credentials(self):
        response = self.client.post("/api/users/login/", self.unregistered_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

