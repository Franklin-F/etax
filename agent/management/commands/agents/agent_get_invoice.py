from lib.service import QueueService
from agent.models import GetInvoice


class GetInvoiceService(QueueService):
    help = 'Get invoice from etax.tianjin.chinatax.gov.cn'
    queue = 'getinvoice'

    def process_data(self):
        model = GetInvoice.objects.get(id=self.one_data['id'])
        model.process()
