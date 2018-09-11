from django.shortcuts import get_object_or_404
from rest_framework import status
from . import BaseTest
from authors.apps.articles.models import Article


class ArticleTests(BaseTest):
    def test_getting_article_from_model(self):
        article_instance = get_object_or_404(Article,title=self.article_data["title"])
        self.assertEqual(str(article_instance), self.article_data["title"])

    def test_article_creation_same_title(self):
        duplicate_article_response = self.create_duplicate_article
        self.assertEqual(duplicate_article_response.status_code, status.HTTP_201_CREATED)

    def test_article_creation(self):
        create_article_response = self.create_article
        self.assertEqual(create_article_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_article_response.data["title"], self.article_data["title"])

    def test_get_all_articles(self):
        get_articles_response = self.get_all_articles
        self.assertEqual(get_articles_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_articles_response.data), 2)

    def test_article_retrieval(self):
        get_article_response = self.get_article
        self.assertEqual(get_article_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_article_response.data["slug"], "this-is-my-title")

    def test_not_existent_article_retrieval(self):
        get_article_response = self.get_not_existing_article
        self.assertEqual(get_article_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article(self):
        get_update_response = self.update_article
        self.assertEqual(get_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_update_response.data["title"], "this is the new title guys")

    def test_delete_article(self):
        delete_article_response = self.delete_article
        self.assertEqual(delete_article_response.status_code, status.HTTP_200_OK)

    def test_delete_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="fake token")
        create_response = self.client.post("/api/article/create", self.article_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
