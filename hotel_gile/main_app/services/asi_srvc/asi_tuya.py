from hotel_gile.settings import TUYA_API_ENDPOINT, TUYA_ACCESS_ID, TUYA_ACCESS_KEY, TUYA_DEVICE_ID
from ..tuya_connector_srvc.ticketencryptor import encrypt_AES_128, decrypt_AES_128
from ..tuya_connector_srvc.openapi import TuyaOpenAPI


def connect():
    openapi = TuyaOpenAPI(TUYA_API_ENDPOINT, TUYA_ACCESS_ID, TUYA_ACCESS_KEY)
    openapi.connect()
    return openapi


def create_password_ticket(openapi):
    response = openapi.post(f"/v1.0/devices/{TUYA_DEVICE_ID}/door-lock/password-ticket")
    return response


def create_tuya_password(reservation):
    if not reservation.locker_password_id:
        openapi = connect()
        password_ticket = create_password_ticket(openapi)

        if password_ticket['success']:
            ticket_key = password_ticket['result']['ticket_key']
            ticket_id = password_ticket['result']['ticket_id']
            key = decrypt_AES_128(ticket_key, TUYA_ACCESS_KEY)
            password = str(reservation.locker_password)
            encrypted_password = encrypt_AES_128(password, key)
            effective_time = int(reservation.check_in.timestamp())
            invalid_time = int(reservation.check_out.timestamp())
            payload = {
                "password": encrypted_password,
                "password_type": "ticket",
                "ticket_id": ticket_id,
                "effective_time": effective_time,
                "invalid_time": invalid_time,
                "name": f"{reservation.id}"
            }
            result = openapi.post(f"/v1.0/devices/{TUYA_DEVICE_ID}/door-lock/temp-password", payload)

            if result['success']:
                reservation.locker_password_id = result['result']['id']


def delete_tuya_password(reservation):
    if reservation.locker_password_id:
        openapi = connect()
        response = openapi.delete(f"/v1.0/devices/{TUYA_DEVICE_ID}/door-lock/temp-passwords/{reservation.locker_password_id}")
        if response['success']:
            reservation.locker_password_id = None

# INFORMATION
# response = openapi.delete(f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-passwords/281015614")
# response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-password/281328414")
# response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-passwords")
# response = openapi.post(f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-passwords/rest-password")
# response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-password/282213514")
# print(response)
