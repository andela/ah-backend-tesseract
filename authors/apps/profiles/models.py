from django.db import models
from ..authentication.models import User


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True,
                            default='https://pixabay.com/en/avatar-person-neutral-man-blank-face-bud-159236/')
    location = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def __str__(self):
        return self.user.username

    def follow(self, followed_profile):
        self.follows.add(followed_profile)

    def unfollow(self, followed_profile):
        self.follows.remove(followed_profile)

    def is_following(self, followed_profile):
        return self.follows.filter(pk=followed_profile.pk).exists()

    def following_user_profiles(self, profile):
        return self.follows.filter(pk=profile.pk)

    def is_followed_user_profiles(self):
        return Profile.objects.filter(follows__user__username=self.user.username)
