import json
from hotel_gile.main_app.models import PaymentLogs
from hotel_gile.settings import FILTER_BODY_KEYS
from functools import wraps


def filter_sensitive_fields(body):
    try:
        return {key: "***Private info***" if key in FILTER_BODY_KEYS else value for key, value in body.items()}
    except Exception as ex:
        return {}


def log_api_call(func):
    @wraps(func)
    def wrapper(self, request):
        request_body = filter_sensitive_fields(request.data)
        response, code = func(self, request_body)

        # Log APi call
        method = request.method
        host = request.META['REMOTE_ADDR']

        log_entry = PaymentLogs(
            host=host,
            method=method,
            code=code,
            request_body=request_body,
            response_body=response.data
        )
        log_entry.save()

        return response
    return wrapper
