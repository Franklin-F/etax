from lib.service import QueueService
from agent.models import Invoicing


class InvoicingService(QueueService):
    help = 'Invoicing in etax.tianjin.chinatax.gov.cn'
    queue = 'invoicing'
    def process_data(self):
        model = Invoicing.objects.get(id=self.one_data['id'])
        model.process()
