# Generated by Django 2.1 on 2018-09-19 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.Notification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('email_sent', models.BooleanField(default=False)),
                ('app_read', models.BooleanField(default=False)),
            ],
        ),
    ]
