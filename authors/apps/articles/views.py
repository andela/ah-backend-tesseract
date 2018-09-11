from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from authors.apps import ApplicationJSONRenderer
from authors.apps.articles.serializers import (ArticlesSerializer,
                                               ArticleSerializer,
                                               DeleteArticleSerializer)

from .models import Article


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