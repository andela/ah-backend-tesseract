from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authors.apps import ApplicationJSONRenderer, update_data_with_user
from authors.apps.articles.serializers import (ArticlesSerializer,
                                               ArticleSerializer,
                                               RatingSerializer,
                                               LikeSerializer,
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
            return Response({"message": "article does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleRatingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    serializer_class = RatingSerializer
    article_serializer = ArticlesSerializer

    def post(self, request):

        data = update_data_with_user(request)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LikeArticleAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    like_serializer = LikeSerializer

    def post(self, request):
        slug = request.data["article"]
        article = get_object_or_404(Article, slug=slug)
        like = request.data["like"]
        user = request.user.id
        data = {"user": user, "article": article.id, "like": like}

        serializer = self.like_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if serializer.action_performed == "created":
            action_status = status.HTTP_201_CREATED
        else:
            action_status = status.HTTP_200_OK
        return Response(serializer.data, status=action_status)
