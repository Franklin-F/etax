from lib.service import QueueService
from agent.models import GetDeduction


class GetDeductionService(QueueService):
    help = 'Get deduction from etax.tianjin.chinatax.gov.cn'
    queue = 'getdeduction'

    def process_data(self):
        model = GetDeduction.objects.get(id=self.one_data['id'])
        model.process()
