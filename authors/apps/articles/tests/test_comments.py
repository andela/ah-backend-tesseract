from rest_framework import status
from . import BaseTransactionTest


class CommentTests(BaseTransactionTest):

    def test_create_comment(self):
        self.assertEqual(self.comment_on_article.status_code, status.HTTP_201_CREATED)

    def test_get_comments(self):
        self.assertEqual(self.get_comments.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        self.update_comment_response = self.client.put("/api/article/" + self.slug + "/comments/1",
                                                       self.updated_comment, format="json")
        self.assertEqual(self.update_comment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.update_comment_response.data["comment"]["body"],
                         self.updated_comment["comment"]["body"])

    def test_delete_comment(self):
        self.delete_comment = self.client.delete("/api/article/" + self.slug + "/comments/1",
                                                 format="json")
        self.assertEqual(self.delete_comment.status_code, status.HTTP_200_OK)

    def test_create_reply(self):
        self.assertEqual(self.reply.status_code, status.HTTP_201_CREATED)

    def test_get_replies(self):
        self.assertEqual(self.get_replies.status_code, status.HTTP_200_OK)

    def test_delete_comment_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.try_delete_comment = self.client.delete("/api/article/" + self.slug + "/comments/1",
                                                     format="json")

        self.assertEqual(self.try_delete_comment.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.try_update = self.client.put("/api/article/" + self.slug + "/comments/1",
                                          self.updated_comment, format="json")
        self.assertEqual(self.try_update.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_comment(self):
        self.invalid_comment = self.client.post("/api/article/" + self.slug + "/comments",
                                                self.invalid_comment_data, format="json")
        self.assertEqual(self.invalid_comment.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_comment_id(self):
        self.invalid_id = self.client.put("/api/article/" + self.slug + "/comments/10",
                                          self.updated_comment, format="json")
        self.assertEqual(self.invalid_id.status_code, status.HTTP_404_NOT_FOUND)
