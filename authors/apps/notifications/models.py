from django.db import models

from authors.apps.articles.models import Article, FavoriteArticle
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile


class Notification(models.Model):

    message = models.CharField(max_length=255, null=False, blank=False)

    title = models.CharField(max_length=125, blank=False, null=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    template = models.CharField(max_length=125, null=False, blank=False, default='default.html')

    date_created = models.DateTimeField(auto_now_add=True)

    def get_subscriptions_on_publishing(self):

        # This method is used when an author with followers publishes new articles
        # and we need to send them a notification by email
        # These subscriptions are for users who are following the author of a given article

        author = self.article.author

        authors_profile = Profile.objects.get(user=author.id)

        authors_followers = authors_profile.is_followed_user_profiles()

        subscriptions = [Subscription.objects.filter(user=profile.user) for profile in authors_followers]

        return subscriptions

    def get_subscriptions_on_comment(self):

        # This method is used when a user favorites an articles
        # and we need to send them a notification by email
        # These subscriptions are for users who are favoriting a given article

        users_favoriting = [favorite.user
                            for favorite in FavoriteArticle.favorites.filter(article=self.article, favorite=True)]

        subscriptions = [Subscription.objects.filter(user=user) for user in users_favoriting]

        return subscriptions


class Subscription(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    by_email = models.BooleanField(default=True)

    by_app = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)


class Recipient(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    email_sent = models.BooleanField(default=False)

    app_read = models.BooleanField(default=False)

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)



