from rest_framework import status
from . import BaseTest
from rest_framework.test import APIClient

class SearchArticleTests(BaseTest):

    def test_search_article_by_author(self):
        response = self.client.get("/api/articles/search/?search=Jacob1234",  format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Jacob1234", str(response.data))

    def test_search_article_by_title(self):
        response = self.client.get("/api/articles/search/?search=this is my title", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("this is my title", str(response.data))


    def test_filter_article_by_author(self):
        response = self.client.get("/api/articles/search/?author=Jacob1234",  format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Jacob1234", str(response.data))

    def test_filter_article_by_not_author(self):
        response = self.client.get("/api/articles/search/?author=1234notin", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([], response.data)

    def test_filter_article_by_title(self):
        response = self.client.get("/api/articles/search/?title=this is my title", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("this is my title", str(response.data))

    def test_an_unauthenticated_user_can_filter_by_author(self):
        self.client = APIClient()
        response = self.client.get("/api/articles/search/?author=fgftfgf",  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([], response.data)

    def test_filter_article_by_a_non_existing_tag(self):
        response = self.client.get("/api/articles/search/?tag=XXXXXXXXXX",  format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([], response.data)

    def test_filter_article_by_tag(self):
        response = self.client.get("/api/articles/search/?tag=Kampala", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
