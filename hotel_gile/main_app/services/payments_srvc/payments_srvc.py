import hotel_gile.settings as settings
import urllib.parse
import requests
from datetime import date

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def generate_payment_link(reservation):
    body = {
        'userName': settings.PAYMENT_USER,
        'password': settings.PAYMENT_PASSWORD,
        'orderNumber': f'{reservation.id}-{reservation.payment_counter}',
        'amount': int(reservation.price * 100),
        'returnUrl': 'https://gile.house/home/',
        'dynamicCallbackUrl': 'https://gile.house/rest/payments/',
        'language': 'bg' if reservation.is_owner_bg() else 'en'
    }

    if date.today() < date(2026, 1, 1):
        body['currency'] = 975  # BGN

    response = requests.post(
        settings.PAYMENT_URL + "/rest/register.do",
        data=body,
        headers=HEADERS
    )

    return response.json()


def check_order_status(reservation):
    body = {
        'userName': settings.PAYMENT_USER,
        'password': settings.PAYMENT_PASSWORD,
        'orderId': reservation.payment_id,
        'language': 'bg'
    }
    response = requests.post(settings.PAYMENT_URL + "/rest/getOrderStatusExtended.do", data=body, headers=HEADERS)

    return response.json()
