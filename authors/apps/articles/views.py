
from rest_framework import generics

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from authors.apps import ApplicationJSONRenderer, update_data_with_user

from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError

from authors.apps.articles.serializers import (ArticlesSerializer, ArticleSerializer, CommentListSerializer,
                                               CommentSerializer,
                                               RatingSerializer,
                                               LikeSerializer,
                                               ReportArticleSerializer,
                                               FavoriteArticleSerializer,
                                               TagSerializer,
                                               BookmarkSerializer)

from authors.apps.notifications.tasks import send_email_notifications

from authors.apps.notifications.utils import create_notification
from authors.apps.notifications.serializers import NotificationSerializer

from .helpers import find_instance, find_parent_comment, find_bookmark, perform_post
from .models import Article, Comment, FavoriteArticle, Tag, ReportedArticles
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class SearchArticlesListAPIView(ListAPIView):
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ArticlesSerializer

    filter_backends = [SearchFilter]
    search_fields = ['title', 'author__username', 'tags__tag']

    def get_queryset(self):

        queryset = self.queryset
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author__username=author)
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag__icontains=tag)
        return queryset


class ArticlesListAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticlesSerializer

    def get(self, request):
        articles = Article.objects.all()
        paginator = Paginator(articles, 5)  # show 5 articles at a time.
        page = request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            articles = paginator.page(1)
        except EmptyPage:
            # if page is out of range, deliver last page of results
            articles = paginator.page(paginator.num_pages)

        serializer = self.serializer_class(articles, many=True)
        return Response({"articles": serializer.data,
                         "number_of_pages": paginator.num_pages,
                         "number_of_articles": paginator.count}, status=status.HTTP_200_OK)


class ArticleAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ApplicationJSONRenderer,)
    serializer_class = ArticleSerializer
    detail_serializer = ArticlesSerializer
    notification_serializer = NotificationSerializer

    def post(self, request):
        article_data = request.data
        article_data["author"] = request.user.id
        context = {'request': request}
        serializer = self.serializer_class(data=article_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Create a notification about the article by this given author

        create_notification('publish_article.html', serializer.instance, request.user)
        send_email_notifications.delay()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        serializer = self.detail_serializer()
        article = find_instance(Article, slug)
        article.set_user_rating(request)
        serializer.instance = article
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        instance = find_instance(Article, slug)
        if instance:
            if instance.author.id == request.user.id or request.user.is_superuser:
                instance.delete()
                return Response({"message": "article deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"message": "article not deleted"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, slug):
        article_data = request.data
        article_data["author"] = request.user.id
        serializer = self.serializer_class(data=article_data, context={'tags': request.data.get('tags', '')})
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

    def post(self, request, slug):
        request.data["user"] = request.user.id
        request.data["article"] = slug
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Article is successfully added to your favorites"},
                        status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        data = update_data_with_user(request, 'user')
        data["article"] = slug
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        favorite = serializer.get_favorite(data)
        favorite.delete()
        return Response({"message": "Article is removed from your favorites"}, status.HTTP_200_OK)


class CommentAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    comment_serializer_class = CommentSerializer
    comment_list_serializer_class = CommentListSerializer
    notification_serializer = NotificationSerializer

    def post(self, request, slug, parent_comment_id=None):
        parent_comment = find_parent_comment(parent_comment_id)

        comment_body = request.data.get('comment', {})

        article = find_instance(Article, slug)
        serializer = self.comment_serializer_class(data=comment_body, context={'author': request.user,
                                                                               'article': article,
                                                                               'parent_comment': parent_comment})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Create a notification about the article by this given author
        create_notification('comment_article.html', article, request.user)
        send_email_notifications.delay()

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


class ReportArticleAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ApplicationJSONRenderer,)
    class_serializer = ReportArticleSerializer

    def post(self, request, slug):
        article = find_instance(Article, slug)
        user = request.user.id
        message = request.data["message"]
        data = {"user": user, "article": article.id, "message": message}

        serializer = self.class_serializer(data=data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        article = find_instance(Article, slug)
        if request.user.is_superuser:
            article_reports = ReportedArticles.objects.filter(article=article.id)
            serializer = self.class_serializer(article_reports, many=True)
            return Response({"reports": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "you do not have access rights"}, status=status.HTTP_401_UNAUTHORIZED)


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class BookmarkAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    bookmark_serializer = BookmarkSerializer

    def post(self, request, slug):
        article = find_instance(Article, slug)

        if find_bookmark(article, request.user):
            raise ValidationError("You have already bookmarked this article")

        serializer = self.bookmark_serializer(data={}, context={"user": request.user,
                                                                "article": article})
        serializer.is_valid()
        serializer.save()

        return Response({"bookmark": serializer.data, "message": "bookmark added"}, status.HTTP_201_CREATED)

    def get(self, request):

        bookmarks = request.user.bookmark_set
        serializer = self.bookmark_serializer(bookmarks, many=True)

        return Response({"bookmarks": serializer.data}, status.HTTP_200_OK)

    def delete(self, request, slug):

        article = find_instance(Article, slug)
        bookmark = find_bookmark(article, request.user)
        if not bookmark:
            raise NotFound("This article is not in your bookmarks")
        bookmark.delete()

        return Response({"message": "Bookmark deleted successfully"}, status.HTTP_200_OK)
