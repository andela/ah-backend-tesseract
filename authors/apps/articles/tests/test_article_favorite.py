
from rest_framework import status
from . import BaseTest


class ArticleTests(BaseTest):

    def favorite_article(self):

        return self.client.post("/api/article/this-is-my-title/favorite", format='json')

    def favorite_delete(self):
        return self.client.delete("/api/article/this-is-my-title/favorite", format='json')

    def unfavorite_post(self):

        return self.client.post("/api/article/this-is-my-title/favorite", format='json')

    def unfavorite_delete(self):
        return self.client.delete("/api/article/this-is-my-title/favorite", format='json')

    def test_favorite_article(self):
        self.assertEqual(self.favorite_article().status_code, status.HTTP_201_CREATED)

    def test_favorite_invalid_article(self):
        self.assertEqual(self.favorite_invalid_article.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_article_twice(self):
        self.favorite_article()
        self.assertEqual(self.favorite_article().status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfavorite_article(self):
        self.favorite_article()
        self.assertEqual(self.unfavorite_delete().status_code, status.HTTP_200_OK)

    def test_unfavorite_article_twice(self):
        self.favorite_article()
        self.unfavorite_delete()
        self.assertEqual(self.unfavorite_delete().status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_with_delete(self):
        self.assertEqual(self.favorite_delete().status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfavorite_with_post(self):
        self.favorite_article()
        self.assertEqual(self.unfavorite_post().status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfavorite_before_favoriting(self):
        response = self.client.delete("/api/article/this-is-my-title/favorite", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

