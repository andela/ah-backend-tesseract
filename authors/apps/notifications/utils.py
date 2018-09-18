from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from authors.apps.authentication.models import User
from authors.apps.notifications.models import Recipient
from authors.apps.notifications.serializers import NotificationSerializer


def create_notification(template, article, user):
    notification_serializer = NotificationSerializer

    # Create a notification about the article by this given author

    if template == 'publish_article.html':
        title = "New article published"
        message = "%s has published a new article [ %s ]" % (user.username, article.title)
    else:
        title = "New comment on Article [ %s ]" % article.title
        message = "%s has commented on article %s " % (user.username, article.title)

    notification_data = {
        "title": title,
        "template": template,
        "message": message,
        "article": article.id
    }
    notification = notification_serializer(data=notification_data)
    notification.is_valid(raise_exception=True)
    notification.save()

    subscriptions = notification.instance.get_subscriptions_on_publishing() \
        if template == 'publish_article.html' \
        else notification.instance.get_subscriptions_on_comment()

    # create recipients to receive this notification

    create_recipients(notification.instance, subscriptions)


def send_email(notification, email, template):
    body = render_to_string(template, {
        'username': User.objects.get(email=email).username,
        'message': notification.message,
        'slug': notification.article.slug,
        'domain': settings.HOST,
        'channel': "by_email",
        'subscribe': False
    })
    email_to_send = EmailMessage(
        notification.title, body, settings.EMAIL_HOST_USER, to=[email]
    )

    email_to_send.send()


def create_recipients(notification, subscriptions):
    for query in subscriptions:
        subscription = query.get()
        user = subscription.user
        data = {"user": user, "notification": notification}
        check_subscription(data, subscription)


def check_subscription(data, subscription):

    if subscription.by_app and subscription.by_email:
        Recipient.objects.create(**data).save()

    elif subscription.by_email and not subscription.by_app:
        data["app_read"] = True
        Recipient.objects.create(**data).save()

    elif subscription.by_app and not subscription.by_email:
        data["email_sent"] = True
        Recipient.objects.create(**data).save()

