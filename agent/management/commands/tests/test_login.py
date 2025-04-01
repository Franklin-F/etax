import time
import traceback
from django.core.management import BaseCommand
from agent.models import Login, GetInvoice, GetInvoiceFile, GetDeduction
from lib.agent.accounts import accounts
from lib.days import get_today
from lib.logger import logger


class BatchLogin(BaseCommand):
    help = 'Batch login'

    def handle(self, *args, **options):
        for account in accounts:
            Login.objects.create(**account)


class RepeatLogin(BaseCommand):
    help = 'Test Login repeatly'

    def handle(self, *args, **options):
        while True:
            try:
                today = get_today()
                logins = set()
                finished_logins = set()

                for account in accounts:
                    if Login.objects.filter(user_id=account['user_id'], status=Login.STATUS_FAIL, addtime__date=today).exists():
                        continue
                    if GetInvoice.objects.filter(user_id=account['user_id'], status=GetInvoice.STATUS_FAIL, addtime__date=today).exists():
                        continue
                    if GetInvoiceFile.objects.filter(user_id=account['user_id'], status=GetInvoiceFile.STATUS_FAIL, addtime__date=today).exists():
                        continue
                    if GetDeduction.objects.filter(user_id=account['user_id'], status=GetDeduction.STATUS_FAIL, addtime__date=today).exists():
                        continue
                    logger.info(f'Add account {account["name"]}')
                    login = Login.objects.create(**account)
                    logins.add(login.id)

                unfinished_logins = logins - finished_logins
                while unfinished_logins:
                    for id in unfinished_logins:
                        login = Login.objects.get(id=id)
                        logger.info(f'{login.id} {login.status} {login.name}')
                        if login.status in [Login.STATUS_DONE, Login.STATUS_FAIL]:
                            finished_logins.add(login.id)
                    unfinished_logins = logins - finished_logins

                    logger.info('Sleep a minute')
                    time.sleep(60)

                logger.info('Sleep an hour')
                time.sleep(3600)

            except Exception as err:
                logger.error(err)
                logger.error(traceback.format_exc())
