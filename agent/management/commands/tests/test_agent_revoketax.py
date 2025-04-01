from django.core.management import BaseCommand
from agent.models import RevokeTax
from lib.agent.accounts import default_account as account


class CreateRevokeTax(BaseCommand):
    help = 'Create RevokeTax Task'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")

    def handle(self, *args, **options):
        RevokeTax.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
        )
