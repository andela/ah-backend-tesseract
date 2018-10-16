from django.db import models
from django.utils.text import slugify

from ..authentication.models import User

import string


class Article(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.CharField(max_length=300)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.TextField(default=None, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('articles.Tag', related_name='articles')

    def __str__(self):
        return self.title

    def get_unique_slug(self):
        if self.slug:
            return

        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.get_unique_slug()
        super().save(*args, **kwargs)

    @property
    def average_rating(self):

        total_ratings = 0
        count = 0
        ratings = Rating.objects.filter(article=self)
        for rate in ratings:
            total_ratings += rate.rating
            count += 1
        return 0 if count == 0 else int(total_ratings/count)

    @property
    def favorites_count(self):
        return FavoriteArticle.favorites.filter(article=self).count()

    @property
    def read_time(self):
        """
        Calculates the amount of time it takes to read an article based on the number of words.
        It assumes an average read time of 275 words per minute.
        """
        words = self.body

        translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
        words_list = words.translate(translator).split()

        num_of_words = len(words_list)

        time_to_read = round(num_of_words/275)
        return str(time_to_read) + " min" if time_to_read > 0 else "less than 1 min"

    @property
    def likes(self):
        likes = self.like_set.filter(like=True).count()
        return likes

    @property
    def dislikes(self):
        dislikes = self.like_set.filter(like=False).count()
        return dislikes

    def comments_on_article(self):
        """
        Returns only comments without a parent comment.
        """
        return self.comment_set.filter(parent_comment=None)

    class Meta:
        ordering = ['id']


class Rating(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)

    date_updated = models.DateTimeField(auto_now=True)

    article = models.ForeignKey(Article, blank=False, null=False, on_delete=models.CASCADE)

    rating = models.IntegerField(blank=False, null=False, default=0)

    rated_by = models.ForeignKey(User, blank=False, null=False,  on_delete=models.CASCADE)


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    body = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FavoriteArticle(models.Model):

    article = models.ForeignKey(Article, blank=False, null=False, on_delete=models.CASCADE)

    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    favorited_at = models.DateTimeField(auto_now_add=True)

    favorites = models.Manager()


class Tag(models.Model):
    tag = models.CharField(max_length=305)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReportedArticles(models.Model):
    article = models.ForeignKey(Article, blank=False, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True)
