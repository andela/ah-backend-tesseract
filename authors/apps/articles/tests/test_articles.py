from django.shortcuts import get_object_or_404
from rest_framework import status
from . import BaseTest
from authors.apps.articles.models import Article


class ArticleTests(BaseTest):
    def test_getting_article_from_model(self):
        article_instance = get_object_or_404(Article, title=self.article_data["title"])
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
        self.assertEqual(len(get_articles_response.data["articles"]), 2)

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

    def test_updating_non_existing_article(self):
        get_update_response = self.update_non_existing_article
        self.assertEqual(get_update_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article_by_different_user(self):
        get_update_response = self.update_article_different_owner
        self.assertEqual(get_update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_article_by_different_user(self):
        delete_article_response = self.delete_article_different_user
        self.assertEqual(delete_article_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_article(self):
        delete_article_response = self.delete_article
        self.assertEqual(delete_article_response.status_code, status.HTTP_200_OK)

    def test_delete_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="fake token")
        create_response = self.client.post("/api/article/create", self.article_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_out_of_range_page_number(self):
        self.paginated_response = self.client.get('/api/articles?page=999')
        self.assertEqual(self.paginated_response.status_code, status.HTTP_200_OK)

    def test_article_read_time(self):
        """Tests if an article of 275 words has a 1 minute read time"""
        article_data = {
            "title": "this is a long article",
            "description": "this is a description",
            "body": "word, "*(275*3)
        }

        create_article_response = self.client.post("/api/article/create", article_data, format="json")
        self.assertEqual(create_article_response.status_code, status.HTTP_201_CREATED)
        read_time = create_article_response.data['read_time']
        self.assertEqual(read_time, "3 min")
    def test_retrieve_tags(self):
        response = self.client.get("/api/article/tags", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
    def test_tag_creation(self):
        response= self.client.post("/api/article/create", self.tag_article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tagsList", str(response.data))

    def test_add_existing_tags_to_an_an_article(self):
        self.client.post("/api/article/create", self.tag_article_data, format="json")
        self.client.post("/api/article/create", self.tag_article_data, format="json")
        response = self.client.get("/api/article/tags", format="json")
        self.assertEqual(4, len(response.data.get('tags')))















