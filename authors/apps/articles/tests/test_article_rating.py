from django.shortcuts import get_object_or_404
from rest_framework import status

from authors.apps.articles.models import Article
from . import BaseTest


class ArticleTests(BaseTest):

    def test_valid_rating(self):
        self.assertEqual(self.rate_article.status_code, status.HTTP_201_CREATED)

    def test_invalid_ratings(self):
        response = self.client.post('/api/article/rating/', self.test_invalid_ratings, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_article_rating(self):
        response = self.client.post('/api/article/rating/', self.test_invalid_article_ratings, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_double_rating(self):
        self.assertEqual(self.rate_article_again.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_by_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.register_second_user_response.data["token"])
        response = self.client.post('/api/article/rating/', self.test_valid_ratings, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_average_rating(self):
        article_instance = get_object_or_404(Article, title=self.article_data["title"])
        self.assertEqual(article_instance.average_rating, 3)
