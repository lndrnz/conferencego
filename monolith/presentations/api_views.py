from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from events.api_views import ConferenceListEncoder
from .models import Presentation
from common.json import ModelEncoder
import json
import pika


def presentation_message(message, queue_name):
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
    )
    connection.close()


def api_list_presentations(request, conference_id):
    presentations = [
        {
            "title": p.title,
            "status": p.status.name,
            "href": p.get_api_url(),
        }
        for p in Presentation.objects.filter(conference=conference_id)
    ]
    return JsonResponse({"presentations": presentations})


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


def api_show_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()
    message = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    presentation_message(json.dumps(message), "presentation_approvals")
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()
    message = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    presentation_message(json.dumps(message), "presentation_rejections")
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
