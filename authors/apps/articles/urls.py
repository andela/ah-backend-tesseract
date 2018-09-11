from django.urls import path
from .views import ArticleAPIView, ArticlesListAPIView

urlpatterns = [
    path("articles", ArticlesListAPIView.as_view(), name="view_articles"),
    path("article/create", ArticleAPIView.as_view(), name="create_article"),
    path("article/edit/<str:slug>", ArticleAPIView.as_view(), name="update_article"),
    path("article/get/<str:slug>", ArticleAPIView.as_view(), name="fetch_article"),
    path("article/delete/<str:slug>", ArticleAPIView.as_view(), name="delete_article"),

    ]
