from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    name = 'authors.apps.profiles'
    label = 'profiles'
    verbose_name = 'Profiles'

    def ready(self):
        import authors.apps.profiles.signal


default_app_config = 'authors.apps.profiles.ProfileAppConfig'
