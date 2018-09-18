from rest_framework import status
from . import BaseTransactionTest


class BookmarksTest(BaseTransactionTest):

    def test_create_bookmark(self):
        create_bookmark = self.client.post('/api/article/' + self.slug + '/bookmark')
        self.assertEqual(create_bookmark.status_code, status.HTTP_201_CREATED)

    def test_create_existing_bookmark(self):
        self.client.post('/api/article/' + self.slug + '/bookmark')
        create_duplicate_bookmark = self.client.post('/api/article/' + self.slug + '/bookmark')
        self.assertEqual(create_duplicate_bookmark.status_code, status.HTTP_400_BAD_REQUEST)
        data = create_duplicate_bookmark.data
        self.assertEqual(data["errors"], ["You have already bookmarked this article"])

    def test_view_bookmarks(self):
        response = self.client.get('/api/articles/bookmarks')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_bookmark(self):
        self.client.post('/api/article/' + self.slug + '/bookmark')
        response = self.client.delete('/api/article/' + self.slug + '/bookmark/delete')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Bookmark deleted successfully")

    def test_delete_nonexistent_bookmark(self):
        response = self.client.delete('/api/article/' + self.slug + '/bookmark/delete')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "This article is not in your bookmarks")
