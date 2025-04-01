from lib.service import QueueService
from agent.models import InvoiceQuota


class InvoiceQuotaService(QueueService):
    help = 'Invoice  Quota in etax.tianjin.chinatax.gov.cn'
    queue = 'invoicequota'

    def process_data(self):
        model = InvoiceQuota.objects.get(id=self.one_data['id'])
        model.process()
