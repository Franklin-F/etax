from lib.curl import Inner
from django.conf import settings


class Crm(Inner):
    host = settings.CRM_HOST
    port = settings.CRM_PORT
    protocol = settings.CRM_PROTOCOL


crm = Crm()
