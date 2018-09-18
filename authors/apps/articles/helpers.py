from rest_framework.exceptions import NotFound
from authors.apps import update_data_with_user
from .models import Article, Comment, Bookmark


def find_instance(model, search_key):
    instance = None
    try:
        if model == Article:
            instance = Article.objects.get(slug=search_key)
        elif model == Comment:
            instance = Comment.objects.get(pk=search_key)
    except Article.DoesNotExist:
        raise NotFound("An article with this slug does not exist")
    except Comment.DoesNotExist:
        raise NotFound("A comment with this id was not found")

    return instance


def find_parent_comment(parent_comment_id):
    if parent_comment_id:
        parent_comment = find_instance(Comment, parent_comment_id)
        if parent_comment.parent_comment is not None:
            # This ensures that any comment made to a reply is only nested one level deep
            parent_comment = parent_comment.parent_comment
    else:
        parent_comment = None

    return parent_comment


def find_bookmark(article, user):
    try:
        bookmark = user.bookmark_set.get(article=article)
    except Bookmark.DoesNotExist:
        bookmark = None

    return bookmark



def perform_post(request, user_key, serializer_class):
    data = update_data_with_user(request, user_key)
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer

