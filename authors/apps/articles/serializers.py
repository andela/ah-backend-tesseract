from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Article
from ..authentication.models import User


class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'description', 'body', 'author']


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'description', 'body', 'author']

    def create(self, validated_data):
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.slug = validated_data.get("slug", instance.get_unique_slug())
        instance.description = validated_data.get("description", instance.description)
        instance.body = validated_data.get("description", instance.description)
        instance.save()
        return instance


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'description', 'slug', 'body', 'author']


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
