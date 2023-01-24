from datetime import datetime
from django.contrib.auth.models import User
from hotel_gile.main_app.api_secrets import api_secrets as secrets


def get_session_language(session):
    import hotel_gile.main_app.language_config as lang_config

    if 'language' not in session:
        session['language'] = lang_config.DEFAULT_LANGUAGE
        session.save()
    return session.get('language')


def default_check_in():
    today = datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime(year, month, day, 14, 00)


def default_check_out():
    today = datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime(year, month, day + 1, 12, 00)


def calculate_reservation_price(reservation):
    DEFAULT_PRICE_PER_PERSION = 30
    discount = 1
    markup = 1
    if reservation.discount:
        if reservation.discount > 0:
            markup = 1 + reservation.discount / 100
        elif reservation.discount < 0:
            discount = 1 - abs(reservation.discount) / 100

    formula = reservation.calc_days * markup * discount * (reservation.room.price -
                                         (DEFAULT_PRICE_PER_PERSION * reservation.room.price_rate *
                                          (reservation.room.room_capacity - max(reservation.total_guests, 2))))
    return round(formula, 1)


def load_reviews():
    import requests
    import json

    url, querystring, headers = secrets.review_api_secrets()
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_data = json.loads(response.text)
    reviews = response_data.get('result')

    return reviews, response.status_code


# ======== RESERVATIONS ==========

def event_template(obj):
    temp_object = datetime.strptime("14:00:00", '%H:%M:%S').time()
    check_in_time = ""
    if obj.check_in.time() != temp_object:
        check_in_time = f'Час на пристигане: {obj.check_in.time()}\n'

    result = {
        'summary': obj.title,
        'description': f'{obj.name} / {obj.phone}\n'
                       f'{obj.adults}+{obj.children} човека - {obj.price}лв.\n'
                       f'{check_in_time}'
                       f'{obj.description}',
        'colorId': str(obj.room.id),
        'start': {
            'date': f'{obj.check_in.date()}',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'date': f'{obj.check_out}',
            'timeZone': 'Europe/Sofia',
        },
    }

    return result


def send_reservation(obj):
    service = secrets.reservation_api_secrets()
    event = event_template(obj)
    event = service.events().insert(calendarId='primary', body=event).execute()

    return event['id']


def update_reservation(obj):
    service = secrets.reservation_api_secrets()
    event = event_template(obj)
    service.events().update(calendarId='primary', eventId=obj.external_id, body=event).execute()


def delete_reservation(obj):
    service = secrets.reservation_api_secrets()
    service.events().delete(calendarId='primary', eventId=obj.external_id).execute()

# def load_reservations():
#     service = secrets.reservation_api_secrets()
#
#     today = datetime.today().isoformat("T", "seconds") + "Z"
#     # end = (today + timedelta(days=90)).isoformat("T", "seconds") + "Z"
#
#     reservations = []
#     while True:
#         events = service.events().list(calendarId='gileood@gmail.com', timeMin=today).execute()
#         for event in events['items']:
#             details = event["description"].split("/")
#             price = re.search('\d+', details[3])
#             room = re.search('\d+', event['summary'])
#             adults, children = details[2].split("+")
#             reservations.append(
#                 {"id": event["id"],
#                  "room": int(room.group(0)),
#                  "name": details[0],
#                  "phone": details[1],
#                  "adults": adults,
#                  "children": children,
#                  "price": int(price.group(0)),
#                  'check_in': event['start']['dateTime'].split("+")[0],
#                  'check_out': event['end']['dateTime'].split("+")[0]
#                  })
#         page_token = events.get('nextPageToken')
#         if not page_token:
#             break
#
#     return reservations


#================ EMAIL ===============

def send_confirmation_email(reservation):
    import base64
    from email.message import EmailMessage
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
    import hotel_gile.main_app.create_email_template as email

    SCOPES = ['https://mail.google.com/']
    creds = Credentials.from_authorized_user_file('hotel_gile/main_app/api_secrets/token.json', SCOPES)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        content = email.create_email(reservation)
        message.set_content(content, subtype='html')

        message['To'] = reservation.email
        message['From'] = 'Guest House GILE<gileood@gmail.com>'
        message['Subject'] = f'Потвърдена резервация/ Confirmed reservation'

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


def send_notification_email(reservation):
    import smtplib
    from hotel_gile.settings import SMTP_USER, SMTP_PASSWORD
    from email.mime.text import MIMEText

    staff_email_list = User.objects.filter(is_staff=True).values_list('email', 'first_name')
    for (receiver, name) in staff_email_list:

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        msg = f"""Здравей, {name}!
        
    Получихте нова резервация.
    Име: {reservation.name},
    Брой гости: {reservation.total_guests},
    От: {reservation.check_in.date()},
    До: {reservation.check_out},
    Нощувки: {reservation.calc_days},
    Телефон: {reservation.phone},
    Email: {reservation.email}"""

        message = MIMEText(msg, 'plain')
        message['Subject'] = "Нова резервация"
        message['From'] = f'* Reservation - Guest House GILE<{SMTP_USER}>'
        session.sendmail(SMTP_USER, receiver, message.as_string())
        session.quit()
