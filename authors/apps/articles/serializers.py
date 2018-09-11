from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Article
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
        fields = ['title', 'slug', 'description', 'body', 'created_at', 'updated_at', 'image', 'author']


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
