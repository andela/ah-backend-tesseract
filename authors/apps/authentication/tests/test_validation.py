from rest_framework import status

from authors.apps.authentication.tests import BaseTest


class ValidationTests(BaseTest):

    def test_missing_email(self):
        """Test whether an error is returned when some required fields are missing"""
        self.user_validate_data["user"].pop("email")

        data = self._helper()
        self.assertEqual(data["errors"]["email"],
                         ["This field is required."])

    def test_missing_username(self):
        """Test whether an error is returned when some required fields are missing"""
        self.user_validate_data["user"].pop("username")

        data = self._helper()
        self.assertEqual(data["errors"]["username"],
                         ["This field is required."])

    def test_missing_password(self):
        """Test whether an error is returned when some required fields are missing"""
        self.user_validate_data["user"].pop("password")

        data = self._helper()
        self.assertEqual(data["errors"]["password"],
                         ["This field is required."])

    def test_invalid_username_length(self):
        """Test whether an error is returned when a short username is provided"""
        self.user_validate_data["user"]["username"] = "lll"

        data = self._helper()
        self.assertEqual(data["errors"]["error"],
                         ['The username should be at least 4 characters long'])

    def test_username_invalid_chars(self):
        """Test whether an error is returned when invalid characters are in the username"""
        self.user_validate_data["user"]["username"] = "ll@l"

        data = self._helper()
        self.assertEqual(data["errors"]["error"],
                         ['Username should only contain letters, numbers, underscores and hyphens'])

    def test_invalid_email(self):
        """Test whether an error is returned if the email is in a wrong format"""
        self.user_validate_data["user"]["email"] = "llll"

        data = self._helper()
        self.assertEqual(data["errors"]["email"],
                         ['Enter a valid email address.'])

    def test_short_password(self):
        """Test whether an error is returned when a short password is used to sign up"""
        self.user_validate_data["user"]["password"] = "p123"

        data = self._helper()
        self.assertEqual(data["errors"]["password"],
                         ['Ensure this field has at least 8 characters.'])

    def test_password_no_digits(self):
        self.user_validate_data["user"]["password"] = "adakfndlnk"

        data = self._helper()
        self.assertEqual(data["errors"]["error"],
                         ['Weak password. The password should contain at least one digit'])

    def test_password_no_chars(self):
        self.user_validate_data["user"]["password"] = "12345678"

        data = self._helper()
        self.assertEqual(data["errors"]["error"],
                         ['Weak password. The password should contain at least one character'])

    def _helper(self):
        """This sends the request to the api and checks if the errors key exists"""
        response = self.client.post("/api/users/", self.user_validate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        return response.data
