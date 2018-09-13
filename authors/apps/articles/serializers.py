import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Article, Rating
from authors.apps.authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class GeneralRepresentation:
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['author'] = UserSerializer(instance.author).data
        return response


class ArticlesSerializer(GeneralRepresentation, serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ['title', 'slug', 'description', 'body',
                  'created_at', 'updated_at', 'image', 'average_rating', 'author']


class ArticleSerializer(GeneralRepresentation, serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'description', 'body', 'author']

    def create(self, validated_data):
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):

        if validated_data["author"].id == instance.author.id:
            instance.title = validated_data.get("title", instance.title)
            instance.slug = validated_data.get("slug", instance.get_unique_slug())
            instance.description = validated_data.get("description", instance.description)
            instance.body = validated_data.get("description", instance.description)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("You are not Authorised to edit this article")


class DeleteArticleSerializer(serializers.Serializer):
    author = serializers.IntegerField()
    slug = serializers.SlugField()

    def validate(self, data):
        author = data.get('author', None)
        slug = data.get("slug", None)

        if not slug:
            raise serializers.ValidationError("article slug needed for delete action")
        instance = get_object_or_404(Article, slug=slug)
        if instance:
            if instance.author.id == author:
                instance.delete()
                return {"author": author, "slug": slug}
            else:
                raise serializers.ValidationError("not authorised to delete this article")


class RatingSerializer(serializers.Serializer):

    article = serializers.SlugField()

    rating = serializers.IntegerField()

    rated_by = serializers.CharField()

    def create(self, validated_data):
        return Rating.objects.create(**validated_data)

    def validate(self, data):
        # Check if article being rated exists
        # Check if user is not the author of the article
        # Users do not rate their own articles
        # User can rate an article once

        try:
            self.article = Article.objects.get(slug=data["article"])
        except Article.DoesNotExist:
            raise serializers.ValidationError("Article you are trying to rate does not exist ")

        if not re.match("[1-5]", str(data["rating"])):
            raise serializers.ValidationError(
                "Your rating should be in range of 1 to 5."
            )

        user = User.objects.get(id=data['rated_by'])

        if self.article.author == user:
            raise serializers.ValidationError("You can not rate an article you authored")

        if Rating.objects.filter(article=self.article, rated_by=user.id):
            raise serializers.ValidationError("You already rated this article")

        data["article"] = self.article
        data["rated_by"] = user

        return data