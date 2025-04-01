from django.core.management import BaseCommand
from agent.models import DownloadInvoice
from lib.days import *
from lib.agent.accounts import accounts, default_account as account


class CreateDownloadInvoice(BaseCommand):
    help = 'Create DownloadInvoice Task'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("begin_date", type=str, nargs='?', help="begin date")
        parser.add_argument("end_date", type=str, nargs='?', help="end date")
        parser.add_argument("--mode", type=str, nargs='?', default='all', help="mode")

    def handle(self, *args, **options):
        DownloadInvoice.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            begin_date=options['begin_date'] or get_first_day_of_last_month(),
            end_date=options['end_date'] or get_last_day_of_last_month(),
            mode=options['mode'],
        )


class BatchDownloadInvoice(BaseCommand):
    help = 'Batch downloadinvoice'

    def handle(self, *args, **options):
        begin_date = get_first_day_of_last_month()
        end_date = get_last_day_of_last_month()
        mode = 'all'
        for account in accounts:
            DownloadInvoice.objects.create(begin_date=begin_date, end_date=end_date, mode=mode, **account)
