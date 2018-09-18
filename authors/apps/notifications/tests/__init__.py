from django.test import TestCase

from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from authors.apps.authentication.models import User


class BaseTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_data = {"user": {"username": "test1",
                                   "email": "test@mail.jake234",
                                   "password": "jakejakeh123"}
                          }

        self.second_user_data = {"user": {"username": "test123",
                                          "email": "test@mali2.jake234383",
                                          "password": "jakfffejakeh1238738"}
                                 }
        self.following_user = {"user": {"username": "test12345",
                                          "email": "test@mail3.jake234383",
                                          "password": "jakejakeh1238738"}
                                 }

        self.article_data = {
            "title": "this is my title",
            "description": "this is a description",
            "body": "this is the body"
        }

        self.article_favorite_data = {
            "article": "this-is-my-title",
            "favorite": True
        }

        self.comment = {
            "comment": {
                "body": "This is a comment"
            }
        }

        self.user1_token = self.register_activate(self.user_data)
        self.user2_token = self.register_activate(self.second_user_data)
        self.user3_token = self.register_activate(self.following_user)

        # user3 follows user1

        self.client.credentials(HTTP_AUTHORIZATION=self.user3_token)
        self.client.post('/api/profiles/test1/follow', format="json")

        # User1 creates article

        self.client.credentials(HTTP_AUTHORIZATION=self.user1_token)
        self.create_article = self.client.post("/api/article/create", self.article_data, format="json")

        # User2 and user3 favorites article

        self.client.credentials(HTTP_AUTHORIZATION=self.user2_token)
        self.client.post("/api/article/favorite", self.article_favorite_data, format="json")

        self.client.credentials(HTTP_AUTHORIZATION=self.user3_token)
        self.client.post("/api/article/favorite", self.article_favorite_data, format="json")

        # User2 unsubscribes from app notifications an user1 from email

        self.client.credentials(HTTP_AUTHORIZATION=self.user2_token)
        self.unsubscribe_app = self.client.put("/api/notifications/by_app/False", format="json")

        self.client.credentials(HTTP_AUTHORIZATION=self.user3_token)
        self.unsubscribe_app = self.client.put("/api/notifications/by_email/False", format="json")

        # User1 comments on article

        self.client.credentials(HTTP_AUTHORIZATION=self.user1_token)
        self.client.post("/api/article/this-is-my-title/comments", self.comment, format="json")


    def register_activate(self, register_data):
        register_response = self.client.post("/api/users/", register_data, format="json")
        user = get_object_or_404(User, email=register_response.data["email"])
        user_id = urlsafe_base64_encode(force_bytes(user.id)).decode()
        token = register_response.data["token"]
        self.client.get("/api/activate/" + user_id + "/" + token + "/account/", format="json")

        return token
