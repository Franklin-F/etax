from lib.service import QueueService
from agent.models import GetInvoiceFile


class GetInvoiceFileService(QueueService):
    help = 'Get invoice from etax.tianjin.chinatax.gov.cn'
    queue = 'getinvoicefile'

    def process_data(self):
        model = GetInvoiceFile.objects.get(id=self.one_data['id'])
        model.process()
