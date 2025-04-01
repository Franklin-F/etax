from lib.service import QueueService
from agent.models import StampDuty


class StampDutyService(QueueService):
    help = 'stamp_duty in etax.tianjin.chinatax.gov.cn'
    queue = 'stampduty'

    def process_data(self):
        model = StampDuty.objects.get(id=self.one_data['id'])
        model.process()
