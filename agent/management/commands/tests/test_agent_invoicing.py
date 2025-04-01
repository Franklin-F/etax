import json
from django.core.management import BaseCommand
from lib.agent.accounts import default_account as account
from agent.models import Invoicing

invoice_data = json.dumps([{
    "项目名称": "橡胶垫",
    "商品和服务税收分类编码": "1070599000000000000",
    "规格型号": "480*200*205mm",
    "单位": "件",
    "商品数量": 4,
    "商品单价": -1000,
    "金额": -4000,
    "税率": 0.13,
    "折扣金额": "",
    "优惠政策类型": ""},
], ensure_ascii=False)
client_name = '大连毅捷船舶技术服务有限公司'
client_code = '91210211728882595Q'
invoice_type = 'no_ordinary_invoice'
business_specific = ''
diff_tax = ''
reduced_tax = ''
remark = ''


class CreateInvoicing(BaseCommand):
    help = 'Create invoicing Task'

    def add_arguments(self, parser):

        parser.add_argument("credit_id", type=str, nargs='?', default=account.credit_id, help="credit id")
        parser.add_argument("name", type=str, nargs='?', default=account.name, help="name")
        parser.add_argument("user_id", type=str, nargs='?', default=account.user_id, help="user id or phone")
        parser.add_argument("password", type=str, nargs='?', default=account.password, help="user password")
        parser.add_argument("invoice_type", type=str, nargs='?', default=invoice_type, help="invoice_type")
        # 特定业务
        parser.add_argument("business_specific", type=str, nargs='?', default=business_specific, help="business_specific")
        parser.add_argument("diff_tax", type=str, nargs='?', default=diff_tax, help="diff_tax", )
        parser.add_argument("reduced_tax", type=str, nargs='?', default=reduced_tax, help="reduced_tax", )

        parser.add_argument("remark", type=str, nargs='?', default=remark, help="remark")
        parser.add_argument("client_code", type=str, nargs='?', default=client_code, help="client_code")
        parser.add_argument("client_name", type=str, nargs='?', default=client_name, help="client_name")
        parser.add_argument("invoice_data", type=str, nargs='?', default=invoice_data, help="invoice_data")

    def handle(self, *args, **options):
        Invoicing.objects.create(
            name=options['name'],
            credit_id=options['credit_id'],
            user_id=options['user_id'],
            password=options['password'],
            client_name=options['client_name'],
            client_code=options['client_code'],
            invoice_type=options['invoice_type'],
            business_specific=options['business_specific'],
            reduced_tax=options['reduced_tax'],
            diff_tax=options['diff_tax'],
            remark=options['remark'],
            invoice_data=options['invoice_data'],
        )
