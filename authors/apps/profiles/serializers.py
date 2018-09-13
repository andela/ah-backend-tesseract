from rest_framework import serializers
# from authors.apps.authentication.serializers import UserProfileSerializer
from .models import Profile
# from ..authentication.serializers import UserProfileSerializer
from ..authentication.models import User


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ('username', 'image')
        read_only_fields = ('username',)


class AuthenticatedProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(allow_blank=True, required=False)
    occupation = serializers.CharField(allow_blank=True, required=False)
    follows = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile

        fields = ('username', 'image', 'bio', 'location','occupation','follows', 'followers', 'following',)
        read_only_fields = ('username',)

    def get_follows(self, instance):
        request = self.context.get('request', None)
        if request is None:
            return False

        follower = request.user.profile
        followed = instance
        return follower.is_following(followed)

    def get_following(self, instance):
        request = self.context.get('request', None)

        if request is not None:
            user_profile = request.user
            followers = Profile.objects.filter(followed_by__user=user_profile)
            temp = []
            for x in followers:
                temp.append(AuthenticatedProfileSerializer(x).data)
            followers = temp
            return (list(followers))

    def get_followers(self, instance):
        request = self.context.get('request', None)
        if request is not None:
            user_profile = request.user.profile
            followings =Profile.objects.filter(follows__user__username=user_profile)
            temp = []
            for x in followings:
                temp.append(AuthenticatedProfileSerializer(x).data)
            followings = temp
            return(list(followings))




