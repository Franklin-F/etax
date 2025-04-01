import time

from django.core.management import BaseCommand
from lib.queue import queues
from lib.days import *


class SendRabbitmq(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--queue", type=str, default='testqueue', help="Queue name")
        parser.add_argument("--host", type=str, default='localhost', help="Host name")

    def handle(self, *args, **options):
        import json
        import pika
        MAX_PRIORITY = 255

        queue_name = options['queue']
        host = options['host']

        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        channel = connection.channel()
        data = json.dumps({'time': get_now_str()})
        channel.queue_declare(queue=queue_name, arguments={"x-max-priority": MAX_PRIORITY})
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=data)
        print(f"[x] Sent message {data}")
        connection.close()


class ReceiveRabbitmq(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--queue", type=str, default='testqueue', help="Queue name")
        parser.add_argument("--host", type=str, default='localhost', help="Host name")

    def handle(self, *args, **options):
        import pika
        MAX_PRIORITY = 255

        queue_name = options['queue']
        host = options['host']

        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, arguments={"x-max-priority": MAX_PRIORITY})

        def callback(ch, method, properties, body):
            print(f" [x] Received {body}")

        channel.basic_consume(queue=queue_name,
                              auto_ack=True,
                              on_message_callback=callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
        connection.close()


class SendQueue(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--queue", type=str, default='testqueue', help="Queue name")
        parser.add_argument("--priority", type=int, default=None, help="Priority")
        parser.add_argument("--num", type=int, default=1, help="Message num")

    def handle(self, *args, **options):
        num = options['num']
        priority = options['priority']
        queue_name = options['queue']
        queue = getattr(queues, queue_name)

        for i in range(num):
            data = {
                'time': get_now_str(),
                'priority': priority,
            }
            queue.send(data, priority=priority)


class ReceiveQueue(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--queue", type=str, default='testqueue', help="Queue name")
        parser.add_argument("--noack", action='store_true', help="Auto ack message")
        parser.add_argument("--forever", action='store_true', help="Receive forever")
        parser.add_argument("--data_interval", type=int, default=0, help="Sleep time")
        parser.add_argument("--idle_interval", type=int, default=1, help="Sleep time")

    def handle(self, *args, **options):
        queue_name = options['queue']
        queue = getattr(queues, queue_name)

        while True:
            message = queue.receive()
            if message is None:
                time.sleep(options['idle_interval'])
                continue
            if not options['noack']:
                queue.ack()
            if not options['forever']:
                break
            time.sleep(options['data_interval'])
