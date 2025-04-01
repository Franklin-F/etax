import time
from lib.logger import logger
from lib.service import QueueService


class ReceiveService(QueueService):
    queue = 'testqueue'

    def process_data(self):
        logger.info(self.one_data)


class SleepService(QueueService):
    queue = 'testqueue'

    def process_data(self):
        logger.info(self.one_data)
        time.sleep(10)


class BugService(QueueService):
    queue = 'testqueue'

    def process_data(self):
        logger.info(self.one_data)
        raise ValueError('raise bug on purpose')
