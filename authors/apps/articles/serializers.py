import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, NotAuthenticated


from .models import Article, Comment, Like, Rating, FavoriteArticle, ReportedArticles, Tag
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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, value):
        return value.tag

class TagRelatedField(serializers.RelatedField):

    def get_queryset(self):
        return Tag.objects.all()

    def to_representation(self, value):
        return value.tag

class ArticlesSerializer(GeneralRepresentation, serializers.ModelSerializer):
    tagsList = TagRelatedField(many=True, required=False, source='tags')

    class Meta:

        model = Article
        fields = ['title', 'slug', 'description', 'body',
                  'created_at', 'updated_at', 'image', 'average_rating', 'author', 'read_time', 'tagsList']



class ArticleSerializer(GeneralRepresentation, serializers.ModelSerializer):
    tagsList = TagRelatedField(many=True, required=False, source='tags')

    class Meta:
        model = Article
        fields = ['title', 'description', 'body', 'author', 'read_time', 'tagsList']

    def create(self, validated_data):
        request = self.context.get('request')
        tags = request.data.get('tags', "")
        tagslist = tags.split(',')
        article = Article.objects.create(**validated_data)
        for tag in tagslist:
            try:
                tag = Tag.objects.get(tag=tag.strip())

                article.tags.add(tag.id)
            except Tag.DoesNotExist:
                article.tags.create(tag=tag.strip())

        return article

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


class FavoriteArticleSerializer(serializers.Serializer):

    article = serializers.SlugField()

    favorite = serializers.BooleanField()

    user = serializers.CharField()

    def create(self, data):
        _data = self.create_or_update(data)

        if isinstance(_data, FavoriteArticle):
            raise serializers.ValidationError("Please use PUT to update the favorite instead of POST")
        else:
            return FavoriteArticle.favorites.create(**_data)

    def update(self, instance, data):
        self.create_or_update(data)
        instance.favorite = data["favorite"]
        instance.save()
        return instance

    def create_or_update(self, data):
        data = self.find_user_article(data)
        query_set = FavoriteArticle.favorites.filter(article=self.article, user=self.user)
        if query_set.exists():
            instance = query_set.get()
            self.handle_existence(instance, data)
            return instance
        return data

    def find_user_article(self, data):
        try:
            self.article = Article.objects.get(slug=data["article"])
            self.user = User.objects.get(id=data["user"])
        except Article.DoesNotExist:
            raise NotFound("Article with that slug does not exist")
        except User.DoesNotExist:
            raise NotFound("User does not exist")

        data["article"] = self.article
        data["user"] = self.user

        return data

    @staticmethod
    def handle_existence(instance, data):
        if instance.favorite == data["favorite"]:
            raise serializers.ValidationError("The article is already in your favorites") \
                if instance.favorite \
                else \
                serializers.ValidationError("The article is already not in your favorites")


class ReportArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportedArticles
        fields = ['user', 'article', 'message']

    def create(self, validated_data):
        return ReportedArticles.objects.create(**validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["user"] = instance.user.username
        response["article"] = instance.article.slug
        return response
