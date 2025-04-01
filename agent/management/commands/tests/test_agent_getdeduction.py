from django.core.management import BaseCommand
from lib.days import *
from agent.models import GetDeduction
from lib.agent.accounts import accounts, default_account as account


class CreateGetDeduction(BaseCommand):
    help = 'Create GetDeduction Task'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("period", type=str, nargs='?', help="period")

    def handle(self, *args, **options):
        GetDeduction.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            period=options['period'] or get_delta_date(months=-2).strftime('%Y-%m'),
        )
