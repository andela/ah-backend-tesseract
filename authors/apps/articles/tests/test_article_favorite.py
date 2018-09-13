
from rest_framework import status
from . import BaseTest


class ArticleTests(BaseTest):

    def favorite_article(self):

        return self.client.post("/api/article/favorite",
                                                {"article": "this-is-my-title-1", "favorite": True}, format='json')

    def unfavorite_post(self):

        return self.client.post("/api/article/favorite",
                                                {"article": "this-is-my-title-1", "favorite": False}, format='json')

    def unfavorite_update(self):
        return self.client.put("/api/article/favorite",
                                                {"article": "this-is-my-title-1", "favorite": False}, format='json')

    def favorite_update(self):
        return self.client.put("/api/article/favorite",
                               {"article": "this-is-my-title-1", "favorite": True}, format='json')

    def test_favorite_article(self):
        self.assertEqual(self.favorite_article().status_code, status.HTTP_201_CREATED)

    def test_favorite_invalid_article(self):
        self.assertEqual(self.favorite_invalid_article.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_article_twice(self):
        self.favorite_article()
        self.assertEqual(self.favorite_update().status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfavorite_article(self):
        self.favorite_article()
        self.assertEqual(self.unfavorite_update().status_code, status.HTTP_200_OK)

    def test_unfavorite_article_twice(self):
        self.unfavorite_post()
        self.assertEqual(self.unfavorite_update().status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_favorite_with_post(self):
        self.favorite_article()
        self.assertEqual(self.favorite_article().status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_article(self):
        response = self.client.put("/api/article/favorite",
                         {"article": "this-is-my-title-inva", "favorite": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_before_favoriting_or_unfavoriting(self):
        response = self.client.put("/api/article/favorite",
                         {"article": "this-is-my-title-1", "favorite": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

