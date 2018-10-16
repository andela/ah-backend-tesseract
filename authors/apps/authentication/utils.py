from authors.apps.notifications.models import Subscription
from .models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404


def custom_send_mail(email, request, template, email_subject):

    site = get_current_site(request)
    db_user = get_object_or_404(User, email=email)

    message = render_to_string(template, {
        'user': db_user,
        'protocol': settings.BACKEND_PROTOCOL,
        'domain': site.domain,
        'user_id': urlsafe_base64_encode(force_bytes(db_user.pk)).decode(),
        'token': db_user.generate_token(),
    })

    email_to_send = EmailMessage(
        email_subject, message, settings.EMAIL_HOST_USER, to=[email]
    )

    email_to_send.send()


def subscribe_user(user, serializer_class):
    if not Subscription.objects.filter(user=user):
        serializer = serializer_class(data={"user": user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()


def send_password_reset_mail(email, request, template, email_subject, callback_url):
    message = render_to_string(template, {
         "callback_url": callback_url,
         "protocol": settings.BACKEND_PROTOCOL
    })

    email_to_send = EmailMessage(
        email_subject, message, settings.EMAIL_HOST_USER, to=[email]
    )
    email_to_send.send()

