from django.core.management import BaseCommand


class Tmp(BaseCommand):
    def handle(self, *args, **options):
        from django.conf import settings
        print('=' * 30)
        print(settings.REST_FRAMEWORK)
        print(type(settings.CRM_HOST), settings.CRM_HOST)
        print(type(settings.CRM_PORT), settings.CRM_PORT)
        print('=' * 30)

        from rest_framework.settings import api_settings
        print(api_settings.DEFAULT_PAGINATION_CLASS)
        print(api_settings.DEFAULT_AUTHENTICATION_CLASSES)
        print('=' * 30)
