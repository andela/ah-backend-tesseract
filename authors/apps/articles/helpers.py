from rest_framework.exceptions import NotFound

from .models import Article, Comment


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
    else:
        parent_comment = None

    return parent_comment
