from rest_framework import serializers

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.notifications.models import Notification, Subscription


class NotificationSerializer(serializers.ModelSerializer):

    message = serializers.CharField()
    template = serializers.CharField()
    title = serializers.CharField()
    article = Article

    class Meta:
        model = Notification
        fields = '__all__'

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):

    user = User
    by_app = serializers.BooleanField(required=False)
    by_email = serializers.BooleanField(required=False)

    class Meta:
        model = Subscription
        fields = '__all__'

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if "by_email" in validated_data:
            instance.by_email = validated_data["by_email"]
        else:
            instance.by_app = validated_data["by_app"]

        instance.save()
        return instance



