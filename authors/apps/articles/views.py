from rest_framework import status

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps import ApplicationJSONRenderer, update_data_with_user

from rest_framework.exceptions import PermissionDenied, NotFound

from authors.apps.articles.serializers import (ArticlesSerializer,
                                               ArticleSerializer,
                                               CommentListSerializer,
                                               CommentSerializer,
                                               RatingSerializer,
                                               LikeSerializer,
                                               DeleteArticleSerializer, FavoriteArticleSerializer)


from .helpers import find_instance, find_parent_comment
from .models import Article, Comment, FavoriteArticle


class ArticlesListAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticlesSerializer

    def get(self, request):
        articles = Article.objects.all()
        serializer = self.serializer_class(articles, many=True)
        return Response({"articles": serializer.data}, status=status.HTTP_200_OK)


class ArticleAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly ,)
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

    def get(self, request, slug):
        serializer = self.detail_serializer()
        serializer.instance = find_instance(Article, slug)
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
        serializer.instance = find_instance(Article, slug)
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


class CommentAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    comment_serializer_class = CommentSerializer
    comment_list_serializer_class = CommentListSerializer

    def post(self, request, slug, parent_comment_id=None):
        parent_comment = find_parent_comment(parent_comment_id)

        comment_body = request.data.get('comment', {})

        article = find_instance(Article, slug)
        serializer = self.comment_serializer_class(data=comment_body, context={'author': request.user,
                                                                               'article': article,
                                                                               'parent_comment': parent_comment})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"comment": serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request, slug, parent_comment_id=None):
        parent_comment = find_parent_comment(parent_comment_id)
        article = find_instance(Article, slug)

        if parent_comment:
            comments = parent_comment.comment_set.all()
            key = "replies_to_comment"
        else:
            comments = article.comments_on_article()
            key = "comments"

        serializer = self.comment_list_serializer_class(comments, many=True)
        return Response({key: serializer.data}, status.HTTP_200_OK)

    def delete(self, request, slug, comment_id):
        find_instance(Article, slug)
        comment = find_instance(Comment, comment_id)

        if request.user.is_superuser or request.user.id == comment.author.id:
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status.HTTP_200_OK)
        else:
            raise PermissionDenied("You are not authorized to delete this comment")

    def put(self, request, slug, comment_id):
        comment_body = request.data.get('comment', {})

        article = find_instance(Article, slug)
        serializer = self.comment_serializer_class(data=comment_body, context={'author': request.user,
                                                                               'article': article})
        comment = find_instance(Comment, comment_id)
        if comment.author.id != request.user.id:
            raise PermissionDenied("You're not authorized to update this article")
        serializer.instance = find_instance(Comment, comment_id)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "comment": serializer.data,
            "message": "comment updated successfully"
        }, status.HTTP_200_OK)


class LikeArticleAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    like_serializer = LikeSerializer

    def post(self, request):
        slug = request.data["article"]
        article = find_instance(Article, slug)
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
