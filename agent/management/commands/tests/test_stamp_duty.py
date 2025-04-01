from django.core.management import BaseCommand
from agent.models import StampDuty
from lib.agent.accounts import default_account as account
import json
import datetime

stamp_duty_data = json.dumps([{
    "credential_name": "例1",
    "term_type": "00|按期申报",
    "number_of_vouchers": "1",
    "tax_items": "101110115|运输合同",
    "tax_certificate_date": "2024-6-30",
    "amount": 375975.27,
    "tax_rate": 0.0003,
    "tax_amount": 112.79,
}, ], ensure_ascii=False)

class CreateStampDuty(BaseCommand):
    help = 'Create Stamp Duty'

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("begin_date", type=str, nargs='?', default=datetime.datetime.strptime('2024-04-01', "%Y-%m-%d"), help="begin date")
        parser.add_argument("end_date", type=str, nargs='?', default=datetime.datetime.strptime('2024-06-30', "%Y-%m-%d"), help="end date")
        parser.add_argument("declaration_type", type=str, nargs='?', default='11|正常申报', help="declaration_type")
        parser.add_argument("from_data", type=str, nargs='?', default=stamp_duty_data, help="from_data")
        parser.add_argument("is_zero_declaration", type=int, nargs='?', default=0, help="is_zero_declaration")

    def handle(self, *args, **options):
        StampDuty.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            begin_date=options['begin_date'],
            end_date=options['end_date'],
            declaration_type=options['declaration_type'],
            from_data=options['from_data'],
            is_zero_declaration=options['is_zero_declaration'],
        )
