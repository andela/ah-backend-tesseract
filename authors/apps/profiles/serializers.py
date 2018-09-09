from rest_framework import serializers

from .models import Profile


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

    class Meta:
        model = Profile
        fields = ('username', 'image', 'bio', 'location', 'occupation')
        read_only_fields = ('username',)