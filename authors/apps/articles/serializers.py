import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, NotAuthenticated
from .models import Article, Rating, FavoriteArticle
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
            raise NotAuthenticated("You are not Authorised to edit this article")


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
            raise NotFound("Article you are trying to rate does not exist ")

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
