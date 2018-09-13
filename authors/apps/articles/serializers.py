import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Article, Comment, Like, Rating

from authors.apps.authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


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


class LikeSerializer(serializers.ModelSerializer):
    action_performed = "created"

    class Meta:
        model = Like
        fields = ['user', 'article', 'like']

    def create(self, validated_data):

        try:
            self.instance = Like.objects.filter(article=validated_data["article"].id, user=validated_data["user"].id)[0:1].get()
        except Like.DoesNotExist:
            return Like.objects.create(**validated_data)

        self.perform_update(validated_data)
        return self.instance

    def perform_update(self, validated_data):
        if self.instance.like == validated_data["like"]:
            self.instance.delete()
            self.action_performed = "deleted"
        else:
            self.instance.like = validated_data["like"]
            self.instance.save()
            self.action_performed = "updated"

class CommentSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    id = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    author = UserSerializer(required=False)
    article = ArticleSerializer(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'author', 'body', 'created_at', 'updated_at']

    def validate(self, data):
        body = data.get('body', None)

        if len(body) < 2:
            raise serializers.ValidationError(
                "Your comment must have at least 2 characters"
            )

        return {
            'body': body,
        }

    def create(self, validated_data):
        author = self.context["author"]
        article = self.context["article"]
        parent_comment = self.context["parent_comment"]
        body = validated_data.get('body')

        return Comment.objects.create(body=body, author=author, article=article, parent_comment=parent_comment)

    def update(self, instance, validated_data):
        instance.body = validated_data.get('body')
        instance.save()
        return instance


class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'updated_at', 'body', 'author']


class CommentListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    replies = ReplySerializer(source='comment_set', many=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'updated_at', 'body', 'author', 'replies']
        depth = 1
