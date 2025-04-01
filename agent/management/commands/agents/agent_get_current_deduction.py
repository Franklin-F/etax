from lib.service import QueueService
from agent.models import GetCurrentDeduction


class GetCurrentDeductionService(QueueService):
    help = 'Get current deduction from etax.tianjin.chinatax.gov.cn'
    queue = 'getcurrentdeduction'

    def process_data(self):
        model = GetCurrentDeduction.objects.get(id=self.one_data['id'])
        model.process()
