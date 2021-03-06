from rest_framework.test import APIClient
from django.test import TestCase, TransactionTestCase

from authors.apps.authentication.models import User


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

        self.tag_article_data = {
            "title": "the Tagging article",
            "description": "This is you",
            "body": "Hello apps",
            "tags": "Hello world, Kampala, Andela Uganda]"
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
            "article": "this-is-my-title",
            "rating": 3
        }
        self.test_invalid_ratings = {
            "article": "this-is-my-title",
            "rating": 9
        }

        self.test_invalid_article_ratings = {
            "article": "this-is-my-title-1-invalid",
            "rating": 3
        }

        self.client = APIClient()

        User.objects.create_user("user_test", "mail@me.com", password="1234sks5678")
        self.user = User.objects.get(email="mail@me.com")
        self.user.is_active = True
        self.user.is_superuser = True
        self.user.save()

        self.super_user_data = {"user": {
            "email": "mail@me.com",
            "password": "1234sks5678"
        }
        }

        self.login_response = self.client.post("/api/users/login/", self.super_user_data, format="json")
        super_user_token = self.login_response.data["token"]

        self.register_response = self.client.post("/api/users/", self.user_data, format="json")
        token = self.register_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        self.create_article = self.client.post("/api/article/create", self.article_data, format="json")

        self.favorite_invalid_article = self.client.post("/api/article/this-is-my-title-invalid/favorite", format='json')

        self.create_duplicate_article = self.client.post("/api/article/create", self.duplicate_article, format="json")
        self.get_all_articles = self.client.get("/api/articles", format="json")
        self.get_article = self.client.get("/api/article/get/this-is-my-title", format="json")
        self.get_not_existing_article = self.client.get("/api/article/get/fake-slug-article", format="json")

        self.update_article = self.client.put("/api/article/edit/this-is-my-title", self.article_update_data,
                                              format="json")
        # delete the duplicate
        self.delete_article = self.client.delete("/api/article/delete/this-is-my-title-1", format="json")

        self.delete_article_with_no_slug = self.client.delete("/api/article/delete/", format="json")

        self.register_second_user_response = self.client.post("/api/users/", self.second_user_data, format="json")

        self.update_non_existing_article = self.client.put("/api/article/edit/this-is-my-title-1-fake",
                                                           self.article_update_data,
                                                           format="json")
        self.report = {"message": "test report"}
        self.test_article_reporting = self.client.post('/api/article/this-is-my-title/report', self.report,
                                                       format="json")

        self.client.credentials(HTTP_AUTHORIZATION=super_user_token)
        self.test_article_reports_get = self.client.get('/api/article/this-is-my-title/report', format="json")

        self.client.credentials(HTTP_AUTHORIZATION=self.register_second_user_response.data["token"])

        self.test_article_reports_get_non_super_user = self.client.get('/api/article/this-is-my-title/report',
                                                                       format="json")

        self.update_article_different_owner = self.client.put("/api/article/edit/this-is-my-title",
                                                              self.article_update_data, format="json")

        self.delete_article_different_user = self.client.delete("/api/article/delete/this-is-my-title",
                                                                format="json")

        self.article_like_data = {
            "article": "this-is-my-title",
            "like": True
        }

        self.test_article_liking = self.client.post("/api/article/like", self.article_like_data, format="json")

        self.article_dislike_data = {
            "article": "this-is-my-title",
            "like": False
        }

        self.article_dislike = self.client.post("/api/article/like", self.article_dislike_data, format="json")

        self.same_like_article_liking = self.client.post("/api/article/like", self.article_dislike_data, format="json")

        self.update_article_different_owner = self.client.put("/api/article/edit/this-is-my-title",
                                                              self.article_update_data,
                                                              format="json")

        # Rate an article
        # Different user rates an article

        self.rate_article = self.client.post('/api/article/rating/', self.test_valid_ratings, format="json")
        self.rate_article_again = self.client.post('/api/article/rating/', self.test_valid_ratings, format="json")
        self.get_article_after_rating = self.client.get("/api/article/get/this-is-my-title")


class BaseTransactionTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user1 = {
            "user":
                {"username": "Jacob1234",
                 "email": "jake@jakeg.jake234",
                 "password": "jakejakeh123"
                 }
        }

        self.user2 = {
            "user": {
                "username": "Jacob123426536",
                "email": "jake@jakeg.jake234383",
                "password": "jakejakeh1238738"
            }
        }
        self.comment = {
            "comment": {
                "body": "This is a comment"
            }
        }

        self.updated_comment = {
            "comment": {
                "body": "Update"
            }
        }

        self.reply_to_comment = {
            "comment": {
                "body": "This is a reply to a comment"
            }
        }

        self.other_article = {
            "title": "how to train a cat",
            "description": "cats are playful",
            "body": "Ever wanted to know?"
        }

        self.invalid_comment_data = {
            "comment": {
                "body": "l"
            }
        }

        self.client = APIClient()

        self.register_user1 = self.client.post("/api/users/", self.user1, format="json")
        token = self.register_user1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        self.register_user2 = self.client.post("/api/users/", self.user2, format="json")
        self.token2 = self.register_user2.data["token"]

        self.create_other_article = self.client.post("/api/article/create", self.other_article, format="json")
        self.slug = "how-to-train-a-cat"
        self.comment_on_article = self.client.post("/api/article/" + self.slug + "/comments",
                                                   self.comment, format="json")
        self.get_comments = self.client.get("/api/article/" + self.slug + "/comments")
        self.get_replies = self.client.get("/api/article/" + self.slug + "/comments/1/replies")
        self.reply = self.client.post("/api/article/" + self.slug + "/comments/1/reply", self.reply_to_comment,
                                      format="json")
