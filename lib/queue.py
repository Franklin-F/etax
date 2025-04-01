import json
import pika
from .logger import logger
from django.conf import settings


MAX_PRIORITY = 255

PRIORITY_CRITICAL = 5
PRIORITY_HIGH = 4
PRIORITY_NORMAL = 3
PRIORITY_LOW = 2
PRIORITY_TRIVIAL = 1


class Connection:
    def __init__(self, url):
        self.params = pika.URLParameters(url)
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()

    def close(self):
        self.channel.close()
        self.connection.close()


class QueueWrapper:
    def __init__(self, connection, queue_name):
        self.connection = connection
        self.queue_name = queue_name
        self.delivery_tag = None
        self.declare()

    def declare(self):
        try:
            self.connection.channel.queue_declare(queue=self.queue_name, arguments={"x-max-priority": MAX_PRIORITY})
        except Exception as err:
            self.connection.connect()
            self.connection.channel.queue_declare(queue=self.queue_name, arguments={"x-max-priority": MAX_PRIORITY})

    def publish(self, message, priority=PRIORITY_NORMAL):
        self.connection.channel.basic_publish(
            properties=pika.BasicProperties(priority=priority),
            exchange='',
            routing_key=self.queue_name,
            body=message)

    def send(self, message, priority=None):
        if not isinstance(message, dict):
            raise ValueError('message must be of type dict')
        if 'retry' not in message:
            message['retry'] = 0
        message = json.dumps(message, ensure_ascii=False)
        logger.debug(f"Queue '{self.queue_name}' Sent '{message}'")
        message = message.encode('utf8')
        try:
            self.publish(message, priority)
        except Exception as err:
            self.connection.connect()
            self.publish(message, priority)

    def receive(self, *args, **kwargs):
        method_frame, header_frame, body = self.get(*args, **kwargs)
        if not method_frame:
            return
        self.delivery_tag = method_frame.delivery_tag
        message = body.decode()
        logger.debug(f"Queue '{self.queue_name}' Received '{message}'")
        message = json.loads(message)
        return message

    def get(self, *args, **kwargs):
        return self.connection.channel.basic_get(queue=self.queue_name, *args, **kwargs)

    def ack(self, delivery_tag=None):
        self.connection.channel.basic_ack(delivery_tag or self.delivery_tag)


class Queue:
    def __init__(self, host='localhost'):
        self.connection = Connection(host)
        self.queues = dict()

    def __getattr__(self, name):
        if name not in self.queues:
            self.queues[name] = QueueWrapper(self.connection, name)
        return self.queues[name]

    def __del__(self):
        self.connection.close()


queues = Queue(settings.QUEUE_URL)

if __name__ == '__main__':
    pass
