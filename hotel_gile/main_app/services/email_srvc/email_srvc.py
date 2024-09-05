from hotel_gile.settings import EMAIL_SRVC_ENDPOINT
import requests
import json


def send_email(payload):
    return requests.post(EMAIL_SRVC_ENDPOINT, data=json.dumps(payload))

