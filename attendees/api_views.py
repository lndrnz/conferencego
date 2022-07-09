from common.json import ModelEncoder
from django.http import JsonResponse

from events.api_views import ConferenceListEncoder

from django.views.decorators.http import require_http_methods

import json

from events.models import Conference

from .models import Attendee


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
        "company_name",
    ]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {"conference": ConferenceListEncoder()}


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.all()
        return JsonResponse(
            {"attendees": attendees},
            safe=False,
            encoder=AttendeeListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee, encoder=AttendeeDetailEncoder, safe=False
        )


def api_show_attendee(request, pk):

    attendee = Attendee.objects.get(id=pk)
    return JsonResponse(
        {"attendee": attendee},
        encoder=AttendeeDetailEncoder,
        safe=False,
    )
