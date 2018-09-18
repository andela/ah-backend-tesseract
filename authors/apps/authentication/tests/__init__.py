import os

from authors.apps.authentication.models import User
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
        token = self.register_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        self.google_invalid_login = {
            "provider": "google-oauth2",
            "access_token": os.environ.get("GOOGLE_INVALID_TOKEN", None)
        }
        self.invalid_provider = {
            "provider": "not_provider",
            "access_token": os.environ.get("GOOGLE_INVALID_TOKEN", None)
        }
        self.facebook_invalid_login = {
            "provider": "facebook",
            "access_token": os.environ.get("FACEBOOK_INVALID_TOKEN", None)
        }
        self.facebook_login = {
            "provider": "facebook",
            "access_token": os.environ.get("FACEBOOK_DEBUG_TOKEN", None)
        }
        self.twitter_login = {
            "provider": "twitter",
            "access_token": os.environ.get("TWITTER_ACCESS_TOKEN", None),
            "access_token_secret": os.environ.get("TWITTER_ACCESS_SECRET", None)
        }
        self.twitter_invalid_login = {
            "provider": "twitter",
            "access_token": os.environ.get("TWITTER_INVALID_TOKEN", None),
            "access_token_secret": os.environ.get("TWITTER_ACCESS_SECRET", None)
        }
        self.twitter_no_secret = {
            "provider": "twitter",
            "access_token": os.environ.get("TWITTER_ACCESS_TOKEN", None)
        }
