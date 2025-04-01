from django.core.management import BaseCommand
from lib.logger import logger
from lib.curl import Inner


class InnerGet(BaseCommand):
    help = 'Test Inner'

    def handle(self, *args, **options):
        inner = Inner(
            host='192.168.110.144',
            protocol='http',
            port=8888,
        )
        req = inner.get('/api/agent/get-invoice/?format=json')
        logger.info(req.status_code)
        logger.info(req.json())


class PostJson(BaseCommand):
    help = 'Post Json'

    def handle(self, *args, **options):
        from agent.models import Login
        login = Login.objects.get(id=1)
        if login.status == Login.STATUS_DONE:
            data = {
                'code': 200,
                'msg': '成功',
                'type': 'login',
                'data': login.result
            }
        elif login.status == Login.STATUS_FAIL:
            data = {
                'code': 500,
                'msg': '失败',
                'type': 'login',
                'data': login.result
            }
        else:
            return

        print(data)

        inner = Inner(
            host='192.168.110.144',
            port=8888,
        )
        req = inner.post('/api/agent/callback/', json=data)
        print(req.status_code)
        print(req.text)

        inner = Inner(
            host='192.168.110.198',
            port=8099,
        )
        req = inner.post('/api/smartaccount/taxApiCallBack', json=data)
        print(req.status_code)
        print(req.text)
        print(req.json())
