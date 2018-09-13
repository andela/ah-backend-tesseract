from django.db import models
from django.utils.text import slugify

from ..authentication.models import User


class Article(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.CharField(max_length=300)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.TextField(default=None, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_unique_slug(self):
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
