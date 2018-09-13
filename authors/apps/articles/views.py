from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.exceptions import NotFound

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authors.apps import ApplicationJSONRenderer, update_data_with_user
from authors.apps.articles.serializers import (ArticlesSerializer,
                                               ArticleSerializer,
                                               DeleteArticleSerializer, 
                                               RatingSerializer, FavoriteArticleSerializer)

from .models import Article, Rating, FavoriteArticle


class ArticlesListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticlesSerializer

    def get(self, request):
        articles = Article.objects.all()
        serializer = self.serializer_class(articles, many=True)
        return Response({"articles": serializer.data}, status=status.HTTP_200_OK)


class ArticleAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    serializer_class = ArticleSerializer
    detail_serializer = ArticlesSerializer
    delete_article_serializer = DeleteArticleSerializer

    def post(self, request):
        article_data = request.data
        article_data["author"] = request.user.id
        serializer = self.serializer_class(data=article_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self,request, slug):
        serializer = self.detail_serializer()
        serializer.instance = get_object_or_404(Article, slug=slug)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        author = request.user.id

        data = {"author": author, "slug": slug}
        serializer = self.delete_article_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": "article deleted successfully"}, status=status.HTTP_200_OK)

    def put(self, request, slug):
        article_data = request.data
        article_data["author"] = request.user.id
        serializer = self.serializer_class(data=article_data)
        try:
            serializer.instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise ValueError("Article does not exist")

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleRatingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    serializer_class = RatingSerializer
    article_serializer = ArticlesSerializer

    def post(self, request):

        serializer = perform_post(request, 'rated_by', self.serializer_class)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteArticleAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    serializer_class = FavoriteArticleSerializer

    def post(self, request):
        return Response(perform_post(request, 'user', self.serializer_class).data, status=status.HTTP_201_CREATED)

    def put(self, request):
        data = update_data_with_user(request, 'user')
        try:
            article = Article.objects.get(slug=data["article"])
            instance = FavoriteArticle.favorites.get(article=article, user=request.user)
        except Article.DoesNotExist:
            raise NotFound("Article with that slug does not exist")
        except FavoriteArticle.DoesNotExist:
            raise NotFound("Use POST to favorite or unfavorite this article")

        serializer = self.serializer_class(data=data)
        serializer.instance = instance
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, data)
        return Response(serializer.data, status=status.HTTP_200_OK)


def perform_post(request, user_key, serializer_class):
    data = update_data_with_user(request, user_key)
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer
