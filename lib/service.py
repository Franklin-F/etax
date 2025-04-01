import sys
import time
import socket
import signal
import datetime
import subprocess
from colorama import Fore, Back, Style, init
from django.core.management.base import BaseCommand
from .logger import logger
import platform

init(autoreset=True)


class BaseService(BaseCommand):
    help = 'Base Service'
    print_info = True
    print_prefix = True
    hostname = socket.gethostname()

    def add_arguments(self, parser):
        parser.add_argument("--status", action='store_true', help="Show status")

    def handle(self, *args, **options):
        if options['status']:
            return self.status()
        else:
            return self.start()

    def std_out(self, content, color=Fore.GREEN):
        if not self.print_info:
            return
        for line in content.split('\n'):
            if self.print_prefix:
                now = datetime.datetime.now()
                time = now.strftime('%Y-%m-%d %H:%M:%S')
                line = f'[{time}] [{self.hostname}] {line}'
            print(color + line)

    def status(self):
        name = ' '.join(sys.argv[:2])
        cmd = f'ps aux | grep python | grep -v "ps aux" | grep "{name}"'
        ret = subprocess.run(cmd, capture_output=True, shell=True)
        out = ret.stdout.decode('utf8').strip()
        if out:
            self.std_out('当前任务的进程列表为：')
            self.std_out('=' * 90)
            self.std_out('USER       PID    %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND', Fore.YELLOW)
            self.std_out('=' * 90)
            self.std_out(out, Fore.YELLOW)
            self.std_out('=' * 90)
            self.std_out('注意：建议使用kill来关闭任务即可, 不建议使用kill -9 来关闭任务!', Fore.RED)
        else:
            self.std_out('当前任务没有执行')

    def start(self):
        if not self.before_start():
            self.std_out('BeforeStart失败', Fore.RED)
            return

        signal.signal(signal.SIGINT, self.recycle)
        signal.signal(signal.SIGTERM, self.recycle)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGQUIT, self.recycle)

        self.after_start()
        self.process()
        self.before_stop()

    def before_start(self):
        logger.debug('Before Start Service')
        return True

    def after_start(self):
        logger.debug('After Start Service')

    def process(self):
        logger.debug('Processing')

    def before_stop(self):
        logger.debug('Before Stop Service')

    def recycle(self, signum=None, frame=None):
        logger.warning(f'Signal received {signum}')
        self.std_out('开始处理回收', Fore.GREEN)
        self.before_stop()
        sys.exit(1)

    def process_exception(self, err):
        logger.error(err)
        self.std_out(str(err), Fore.RED)
        self.recycle()


class Service(BaseService):
    help = 'Service'
    timeout = 3600
    data_interval = 0
    idle_interval = 1

    def __init__(self):
        super().__init__()
        self.one_data = None
        self.is_processed = False

    def process(self):
        start_time = time.time()
        while True:
            self.one_data = self.get_data()
            self.is_processed = False
            if self.one_data is not None:
                if not self.before_process():
                    continue
                self.process_data()
                self.after_process()
                self.is_processed = True
                time.sleep(self.data_interval)
            else:
                time.sleep(self.idle_interval)

            if time.time() - start_time >= self.timeout:
                break

    def before_process(self):
        logger.debug('Before Process')
        return True

    def after_process(self):
        logger.debug('After Process')

    def get_data(self):
        pass

    def process_data(self):
        pass


class QueueService(Service):
    help = 'Queue Service'
    queue = None
    max_retry = 5

    def __init__(self):
        super().__init__()
        if not self.queue:
            raise ValueError('需指定队列名称')
        from lib.queue import queues
        self.queueobj = getattr(queues, self.queue)

    def get_data(self):
        data = self.queueobj.receive()
        if not data:
            return
        retry = data.get('retry', 0)
        if retry >= self.max_retry:
            self.std_out(f'超出最大重试次数：{retry}', Fore.RED)
            return
        return data

    def process_data(self):
        logger.debug(f'Processing {self.queueobj.delivery_tag} : {self.one_data}')

    def after_process(self):
        logger.debug(f'Processed {self.queueobj.delivery_tag} : {self.one_data}')
        self.queueobj.ack()

    def before_stop(self):
        super().before_stop()
        if not self.is_processed:
            self.failure()

    def failure(self):
        self.std_out('开始处理错误', Fore.GREEN)


class QueryService(Service):
    query = None

    def get_data(self):
        pass

    def process_data(self):
        pass
