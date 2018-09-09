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

    def __str__(self):
        return self.user.username

