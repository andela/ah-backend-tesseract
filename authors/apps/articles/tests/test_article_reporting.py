from rest_framework import status
from . import BaseTest


class ArticleReportTests(BaseTest):
    def test_valid_article_reporting(self):
        report_article = self.test_article_reporting
        self.assertEqual(report_article.status_code, status.HTTP_201_CREATED)

    def test_article_reports(self):
        report_article = self.test_article_reports_get
        self.assertEqual(report_article.status_code, status.HTTP_200_OK)

    def test_article_reports_not_superuser(self):
        report_article = self.test_article_reports_get_non_super_user
        self.assertEqual(report_article.status_code, status.HTTP_401_UNAUTHORIZED)
