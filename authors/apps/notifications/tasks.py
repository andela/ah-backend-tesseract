from celery.task import task

from authors.apps.notifications.models import Recipient
from authors.apps.notifications.utils import send_email


@task()
def send_email_notifications():

    recipients = Recipient.objects.filter(email_sent=False)

    for recipient in recipients:
        notification = recipient.notification
        send_email(notification, recipient.user.email, notification.template)
        recipient.email_sent = True
        recipient.save()

