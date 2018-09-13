import os

from authors.apps.authentication.models import User
from rest_framework.test import APIClient
from django.test import TestCase


class BaseTest(TestCase):

    def setUp(self):
        self.user_data = {"user": {"username": "Jacob1234",
                                   "email": "jake@jakeg.jake234",
                                   "password": "jakejakeh123"}
                          }

        self.second_user_data = {"user": {"username": "Jacob123426536",
                                   "email": "jake@jakeg.jake234383",
                                   "password": "jakejakeh1238738"}
                          }

        self.article_data = {
            "title": "this is my title",
            "description": "this is a description",
            "body": "this is the body"
        }

        self.duplicate_article = {
            "title": "this is my title",
            "description": "this is a description for the second one",
            "body": "this is the body for the second one"
        }

        self.article_update_data = {
            "title": "this is the new title guys",
            "description": "what do you think",
            "body": "this is the body"
        }

        self.test_valid_ratings = {
            "article": "this-is-my-title-1",
            "rating": 3
        }
        self.test_invalid_ratings = {
            "article": "this-is-my-title-1",
            "rating": 9
        }

        self.test_invalid_article_ratings = {
            "article": "this-is-my-title-1-invalid",
            "rating": 3
        }

        self.client = APIClient()

        self.register_response = self.client.post("/api/users/", self.user_data, format="json")
        token = self.register_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        self.create_article = self.client.post("/api/article/create", self.article_data, format="json")
        self.create_duplicate_article = self.client.post("/api/article/create", self.duplicate_article, format="json")
        self.get_all_articles = self.client.get("/api/articles", format="json")
        self.get_article = self.client.get("/api/article/get/this-is-my-title", format="json")
        self.get_not_existing_article = self.client.get("/api/article/get/fake-slug-article", format="json")

        self.update_article = self.client.put("/api/article/edit/this-is-my-title", self.article_update_data,
                                              format="json")

        self.delete_article = self.client.delete("/api/article/delete/this-is-the-new-title-guys", format="json")

        self.delete_article_with_no_slug = self.client.delete("/api/article/delete/", format="json")

        self.register_second_user_response = self.client.post("/api/users/", self.second_user_data, format="json")

        self.update_non_existing_article = self.client.put("/api/article/edit/this-is-my-title-1-fake",
                                                           self.article_update_data,
                                                           format="json")

        self.client.credentials(HTTP_AUTHORIZATION=self.register_second_user_response.data["token"])
        self.update_article_different_owner = self.client.put("/api/article/edit/this-is-my-title-1",
                                                              self.article_update_data, format="json")

        self.delete_article_different_user = self.client.delete("/api/article/delete/this-is-my-title-1",
                                                                format="json")

        self.article_like_data = {
            "article": "this-is-my-title-1",
            "like": True
        }

        self.test_article_liking = self.client.post("/api/article/like", self.article_like_data, format="json")

        self.article_dislike_data = {
            "article": "this-is-my-title-1",
            "like": False
        }

        self.article_dislike = self.client.post("/api/article/like", self.article_dislike_data, format="json")

        self.same_like_article_liking = self.client.post("/api/article/like", self.article_dislike_data, format="json")


        # Rate an article
        # Different user rates an article

        self.rate_article = self.client.post('/api/article/rating/', self.test_valid_ratings, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=self.register_response.data["token"])
        self.rate_article_again = self.client.post('/api/article/rating/', self.test_valid_ratings, format="json")
