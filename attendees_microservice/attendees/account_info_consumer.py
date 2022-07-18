from datetime import datetime
import json
import queue
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from datetime import date


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()

from attendees.models import AccountVO

def update_AccountVO(ch, method, properties, body):
    content = json.loads(body)
    first_name = content["first_name"]
    last_name = content ["last_name"]
    email = content["email"]
    is_active = content["is_active"]
    updated_string = content["updated"]
    updated = date.fromisoformat(updated_string)
    if is_active:
        AccountVO.objects.update_or_create(first_name=first_name, last_name=last_name, email=email, is_active=is_active, updated=updated)
    else:
        AccountVO.delete(email=email)
    
while True:
    try:
        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue="")
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message
        )
        connection.close()
