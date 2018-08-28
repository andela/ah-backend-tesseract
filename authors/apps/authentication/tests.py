from django.test import TestCase
from .models import User


class AuthenticationTests(TestCase):

    def setUp(self):
        User.objects.create_user("user_test", "mail@me.com", password="1234")
        self.user = User.objects.get(id=1)

    def test_username_label(self):

        field_label = self.user._meta.get_field('username').verbose_name
        self.assertEquals(field_label, 'username')

    def test_get_full_name(self):
        self.assertEquals("user_test", self.user.get_full_name)

    def test_get_short_name(self):
        self.assertEquals("user_test", self.user.get_short_name())