import hotel_gile.settings as settings
import urllib.parse
import requests

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def generate_payment_link(reservation):
    body = {
        'amount': int(reservation.price * 100),
        'currency': 975,
        'userName': settings.PAYMENT_USER,
        'password': settings.PAYMENT_PASSWORD,
        'returnUrl': 'https://gile.house/home/',
        'orderNumber': f'{reservation.id}-{reservation.payment_counter}',
        'dynamicCallbackUrl': 'https://gile.house/rest/payments/',
        'language': reservation.is_owner_bg()
    }
    encoded_body = urllib.parse.urlencode(body)
    response = requests.post(settings.PAYMENT_URL + "/rest/register.do", data=encoded_body, headers=HEADERS)

    return response.json()


def check_order_status(reservation):
    body = {
        'userName': settings.PAYMENT_USER,
        'password': settings.PAYMENT_PASSWORD,
        'orderId': reservation.payment_id,
        'language': 'bg'
    }
    encoded_body = urllib.parse.urlencode(body)
    response = requests.post(settings.PAYMENT_URL + "/rest/getOrderStatusExtended.do", data=encoded_body, headers=HEADERS)

    return response.json()
