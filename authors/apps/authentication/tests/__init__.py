from ..models import User
from rest_framework.test import APIClient
from django.test import TestCase


class BaseTest(TestCase):

    def setUp(self):
        self.user_data = {"user": {"username": "Jacob1",
                                   "email": "jake@jakeg.jake",
                                   "password": "jakejakeh1"}
                          }

        self.login_data_email = {"user": {"email": "mail@me.com",
                                          "password": "12345678"}
                                 }

        self.unregistered_user_data = {"user": {"email": "jake@hhd.jake",
                                                "password": "jakeakeh1"}
                                       }

        self.user_validate_data = {"user": {"username": "llll",
                                            "email": "l@gmail.com",
                                            "password": "p1234567"
                                            }
                                   }

        self.user_update_data = {"user": {"username": "user_test2",
                                          "email": "mail@me.com",
                                          "password": "p12345678"
                                          }}

        self.client = APIClient()

        User.objects.create_user("user_test", "mail@me.com", password="12345678")
        self.user = User.objects.get(email="mail@me.com")
        self.user.is_active = True
        self.user.save()

        self.register_response = self.client.post("/api/users/", self.user_data, format="json")
        self.login_response = self.client.post("/api/users/login/", self.login_data_email, format="json")
        token = self.login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)
