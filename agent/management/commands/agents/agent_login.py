from lib.service import QueueService
from agent.models import Login


class LoginService(QueueService):
    help = 'Login in tpass.tianjin.chinatax.gov.cn'
    queue = 'login'

    def process_data(self):
        model = Login.objects.get(id=self.one_data['id'])
        model.process()
