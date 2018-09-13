from rest_framework import status
from . import BaseTest


class ArticleLikeTests(BaseTest):
    def test_valid_article_liking(self):
        like_article = self.test_article_liking
        self.assertEqual(like_article.status_code, status.HTTP_201_CREATED)

    def test_article_dislike(self):
        article_dislike = self.article_dislike
        self.assertEqual(article_dislike.status_code, status.HTTP_200_OK)

    def test_same_like_article_liking(self):
        same_like_article_liking = self.same_like_article_liking
        self.assertEqual(same_like_article_liking.status_code, status.HTTP_200_OK)
