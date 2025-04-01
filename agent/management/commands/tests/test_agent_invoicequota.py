from django.core.management import BaseCommand
from lib.agent.accounts import default_account as account
from lib.days import get_first_day_of_last_month, get_last_day_of_last_month
from agent.models import InvoiceQuota


class CreateInvoiceQuota(BaseCommand):
    help = 'Create invoice_quota Task'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("begin_date", type=str, nargs='?', help="begin date")
        parser.add_argument("end_date", type=str, nargs='?', help="end date")

    def handle(self, *args, **options):
        InvoiceQuota.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            begin_date=options['begin_date'] or get_first_day_of_last_month(),
            end_date=options['end_date'] or get_last_day_of_last_month()
        )
