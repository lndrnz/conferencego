import json
import queue
import pika
import django
import os
import sys
from django.core.mail import send_mail
from pika.exceptions import AMQPConnectionError
import time


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

while True:
    try:
        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue="presentation_approvals")
        channel.queue_declare(queue="presentation_rejections")

        def process_approvals(ch, method, properties, body):
            message = json.loads(body)
            email = message["presenter_email"]
            name = message["presenter_name"]
            title = message["title"]
            send_mail(
                "Your presentation has been accepted",
                f"{name}, we're happy to tell you that your presentation {title} has been accepted",
                "admin@conference.go",
                [email],
                fail_silently=False,
            )

        def process_rejections(ch, method, properties, body):
            message = json.loads(body)
            email = message["presenter_email"]
            name = message["presenter_name"]
            title = message["title"]
            send_mail(
                "Your presentation has been rejected",
                f"{name}, we're sorry to tell you that your presentation {title} has been rejected",
                "admin@conference.go",
                [email],
                fail_silently=False,
            )

        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approvals,
            auto_ack=True,
        )
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejections,
            auto_ack=True,
        )

        channel.start_consuming()

    except AMQPConnectionError:
        print("Unable  to connect")
        time.sleep(2.0)
