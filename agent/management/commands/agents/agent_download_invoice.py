from lib.service import QueueService
from agent.models import DownloadInvoice


class DownloadInvoiceService(QueueService):
    help = 'Download invoice from etax.tianjin.chinatax.gov.cn'
    queue = 'downloadinvoice'

    def process_data(self):
        model = DownloadInvoice.objects.get(id=self.one_data['id'])
        model.process()
