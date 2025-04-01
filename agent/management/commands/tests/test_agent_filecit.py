from django.core.management import BaseCommand
from lib.agent.accounts import default_account as account
from agent.models import FileCit


class CreateFileCit(BaseCommand):
    help = 'Create FileCit Task'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("begin_staff", type=int, nargs='?', default=0, help="begin staff num")
        parser.add_argument("end_staff", type=int, nargs='?', default=0, help="end staff num")

    def handle(self, *args, **options):
        FileCit.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            begin_staff=options['begin_staff'],
            end_staff=options['end_staff'],
        )
