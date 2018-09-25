from django.urls import path

from .views import (ArticleAPIView,
                    ArticlesListAPIView,
                    ArticleRatingAPIView,
                    LikeArticleAPIView,
                    CommentAPIView,
                    ReportArticleAPIView,
                    FavoriteArticleAPIView,
                    TagListAPIView,
                    SearchArticlesListAPIView,
                    BookmarkAPIView)


urlpatterns = [
    path("articles", ArticlesListAPIView.as_view(), name="view_articles"),
    path("article/create", ArticleAPIView.as_view(), name="create_article"),
    path("article/edit/<str:slug>", ArticleAPIView.as_view(), name="update_article"),
    path("article/get/<str:slug>", ArticleAPIView.as_view(), name="fetch_article"),
    path("article/delete/<str:slug>", ArticleAPIView.as_view(), name="delete_article"),
    path("article/like", LikeArticleAPIView.as_view()),
    path("article/rating/", ArticleRatingAPIView.as_view(), name="rate_article"),

    path("article/<str:slug>/comments", CommentAPIView.as_view(), name="add_or_get_comments"),
    path("article/<str:slug>/comments/<int:comment_id>", CommentAPIView.as_view(), name="update_or_delete_comment"),
    path("article/<str:slug>/comments/<int:parent_comment_id>/reply", CommentAPIView.as_view(),
         name="reply_to_comment"),
    path("article/<str:slug>/comments/<int:parent_comment_id>/replies", CommentAPIView.as_view(),
         name="get_all_replies"),
    path("article/<str:slug>/favorite", FavoriteArticleAPIView.as_view(), name="favorite_article"),

    path("article/<str:slug>/report", ReportArticleAPIView.as_view(), name="report_article"),
    path("article/tags", TagListAPIView.as_view(), name="article-tags"),
    path("articles/search/", SearchArticlesListAPIView.as_view(), name="search_articles"),

    path("article/<str:slug>/bookmark", BookmarkAPIView.as_view(), name="bookmark_article"),
    path("articles/bookmarks", BookmarkAPIView.as_view(), name="bookmarks"),
    path("article/<str:slug>/bookmark/delete", BookmarkAPIView.as_view(), name="delete_bookmark"),
    ]
