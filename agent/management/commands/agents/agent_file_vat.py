from lib.service import QueueService
from agent.models import FileVat


class FileVatService(QueueService):
    help = 'File Vat in etax.tianjin.chinatax.gov.cn'
    queue = 'filevat'

    def process_data(self):
        model = FileVat.objects.get(id=self.one_data['id'])
        model.process()
