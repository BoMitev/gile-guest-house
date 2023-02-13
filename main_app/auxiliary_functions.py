import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.models import User
from hotel_gile.settings import SMTP_USER, SMTP_PASSWORD
from hotel_gile.main_app.api_secrets import api_secrets as secrets


def get_session_language(session):
    import hotel_gile.main_app.language_config as lang_config

    if 'language' not in session:
        session['language'] = lang_config.DEFAULT_LANGUAGE
        session.save()
    return session.get('language')


def default_check_in():
    today = datetime.datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime.datetime(year, month, day, 14, 00)


def default_check_out():
    today = datetime.datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime.datetime(year, month, day, 12, 00) + datetime.timedelta(days=1)


def calculate_reservation_price(reservation):
    from hotel_gile.main_app.models import RoomPrice

    if not reservation.discount:
        discount = 0
    else:
        discount = reservation.discount

    obj = RoomPrice.objects.get(room=reservation.room, persons=reservation.total_guests)

    formula = reservation.calc_days * (obj.price + discount)

    return round(formula, 2)


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
    temp_object = datetime.datetime.strptime("14:00:00", '%H:%M:%S').time()
    check_in_time = ""
    if obj.check_in.time() != temp_object:
        check_in_time = f'Час на пристигане: {obj.check_in.time()}\n'

    result = {
        'summary': obj.title,
        'description': f'{obj.name} / {obj.phone}\n'
                       f'{obj.adults}+{obj.children} човека\n'
                       f'{obj.calc_days} x {obj.price/obj.calc_days:.2f} = {obj.price:.2f}лв.\n'
                       f'{check_in_time}'
                       f'{obj.description}',
        'colorId': str(obj.room.id),
        'start': {
            'date': f'{obj.check_in.date()}',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'date': f'{obj.check_out.date()}',
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


# ================ EMAIL ===============

def send_confirmation_email(reservation):
    import hotel_gile.main_app.create_email_template as email
    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        message = MIMEMultipart('alternative')
        message['Subject'] = f'Потвърдена резервация/ Confirmed reservation'
        message['From'] = f'Guest House GILE<{SMTP_USER}>'
        msg = MIMEText(email.create_email(reservation), 'html')

        message.attach(msg)
        session.sendmail(SMTP_USER, reservation.email, message.as_string())
        session.quit()
    except Exception as ex:
        print(ex)


def send_notification_email(reservation):
    staff_email_list = [x[0] for x in User.objects.filter(is_staff=True).values_list('email') if x[0]]
    if not staff_email_list:
        return

    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        msg = f"""Получихте нова резервация.
    Име: {reservation.name},
    Брой гости: {reservation.total_guests},
    От: {reservation.check_in.date()},
    До: {reservation.check_out.date()},
    Нощувки: {reservation.calc_days},
    Телефон: {reservation.phone}"""
        if reservation.email:
            msg += f",\nEmail: {reservation.email}"

        message = MIMEText(msg, 'plain')
        message['Subject'] = "Нова резервация"
        message['From'] = f'* Reservation - Guest House GILE<{SMTP_USER}>'
        session.sendmail(SMTP_USER, staff_email_list, message.as_string())
        session.quit()
    except Exception as ex:
        print(ex)
