from lib.service import QueueService
from agent.models import FileBsis


class FileBsisService(QueueService):
    help = 'File Balance Sheet & Income Statement in etax.tianjin.chinatax.gov.cn'
    queue = 'filebsis'

    def process_data(self):
        model = FileBsis.objects.get(id=self.one_data['id'])
        model.process()
