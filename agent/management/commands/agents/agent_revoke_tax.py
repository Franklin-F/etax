from lib.service import QueueService
from agent.models import RevokeTax


class RevokeTaxService(QueueService):
    help = 'Revoke Tax in etax.tianjin.chinatax.gov.cn'
    queue = 'revoketax'

    def process_data(self):
        model = RevokeTax.objects.get(id=self.one_data['id'])
        model.process()
