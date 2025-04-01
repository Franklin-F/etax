from lib.service import QueueService
from agent.models import FileCit


class FileCitService(QueueService):
    help = 'File Cit in etax.tianjin.chinatax.gov.cn'
    queue = 'filecit'

    def process_data(self):
        model = FileCit.objects.get(id=self.one_data['id'])
        model.process()
