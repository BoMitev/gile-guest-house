import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.models import User
from hotel_gile.settings import SMTP_USER, SMTP_PASSWORD
from hotel_gile.main_app.api_secrets import api_secrets as secrets
import hotel_gile.main_app.create_email_template as email


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

    return datetime(year, month, day, 12, 00) + timedelta(days=1)


def load_reviews():
    import requests
    import json

    url, querystring, headers = secrets.review_api_secrets()
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_data = json.loads(response.text)
    reviews = response_data.get('result')

    return reviews, response.status_code


# ======== RESERVATIONS ==========

def event_template(reservation, rooms):
    temp_object = datetime.strptime("14:00:00", '%H:%M:%S').time()
    check_in_time = ""
    if reservation.check_in.time() != temp_object:
        check_in_time = f'Час на пристигане: {reservation.check_in.time()}\n'

    description = f'{reservation.name.title()} / {reservation.phone}\n'

    for room in rooms:
        description += f'{room.title}\n{room.adults}+{room.clean_children()} човека\n{room.stay} x {room.total_price/room.stay:.2f} = {room.total_price:.2f}лв.\n\n'
    description += f'{check_in_time}{reservation.description}'

    result = {
        'summary': reservation.title,
        'description': description,
        'colorId': str(rooms[0].room.id),
        'start': {
            'date': f'{reservation.check_in.date()}',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'date': f'{reservation.check_out.date()}',
            'timeZone': 'Europe/Sofia',
        },
    }

    return result


def send_update_reservation(reservation, rooms):
    if reservation.status > 0:
        service = secrets.reservation_api_secrets()
        event = event_template(reservation, rooms)
        if reservation.external_id:
            pass
            #service.events().update(calendarId='primary', eventId=reservation.external_id, body=event).execute()
        else:
            pass
            #response = service.events().insert(calendarId='primary', body=event).execute()
            #reservation.external_id = response['id']
            #reservation.save()


def delete_reservation(reservation):
    if reservation.external_id:
        try:
            service = secrets.reservation_api_secrets()
            #service.events().delete(calendarId='primary', eventId=reservation.external_id).execute()
        except Exception as ex:
            print(ex)
        finally:
            pass
            #reservation.external_id = None
            #reservation.save()


# ================ EMAIL ===============

def send_confirmation_email(reservation, all_rooms):
    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        message = MIMEMultipart('alternative')
        message['Subject'] = f'Потвърдена резервация/ Confirmed reservation'
        message['From'] = f'Guest House GILE<{SMTP_USER}>'
        msg = MIMEText(email.confirm_email(reservation, all_rooms), 'html')

        message.attach(msg)
        session.sendmail(SMTP_USER, [reservation.email, "guest@gile.house"], message.as_string())
    except Exception as ex:
        print(ex)
        return False
    else:
        reservation.email_sent = True
        return True
    finally:
        session.quit()
        reservation.save()


def send_reject_email(reservation):
    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        message = MIMEMultipart('alternative')
        message['Subject'] = f'Отхвърлена резервация/ Services unavailable'
        message['From'] = f'Guest House GILE<{SMTP_USER}>'
        msg = MIMEText(email.reject_email(reservation), 'html')
        message.attach(msg)
        session.sendmail(SMTP_USER, reservation.email, message.as_string())
    except Exception as ex:
        print(ex)
    finally:
        session.quit()


def send_notification_email(event):
    from hotel_gile.main_app.forms import ContactForm, ReservationForm

    staff_email_list = [x[0] for x in User.objects.filter(is_staff=True).values_list('email') if x[0]]
    if not staff_email_list:
        return

    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        if isinstance(event, ReservationForm):
            msg = f"""Получихте нова резервация.
Име: {event.cleaned_data['name']},
Брой гости: {event.cleaned_data['adults'] + event.cleaned_data['children']},
Брой стаи: {event.cleaned_data['rooms']},
От: {event.cleaned_data['check_in'].date().strftime("%d.%m.%Y")},
До: {event.cleaned_data['check_out'].date().strftime("%d.%m.%Y")},
Нощувки: {abs(event.cleaned_data['check_in'].date() - event.cleaned_data['check_out'].date()).days},
Телефон: {event.cleaned_data['phone']}"""
            if event.cleaned_data['email']:
                msg += f",\nEmail: {event.cleaned_data['email']}"

            message = MIMEText(msg, 'plain')
            message['Subject'] = "Нова резервация"
            message['From'] = f'* Reservation - Guest House GILE<{SMTP_USER}>'
        elif isinstance(event, ContactForm):
            msg = f"""Получихте ново запитване. 
Име: {event.cleaned_data['name']},
Имейл: {event.cleaned_data['email']},
Запитване: {event.cleaned_data['message']}
"""
            message = MIMEText(msg, 'plain')
            message['Subject'] = "Ново запитване"
            message['From'] = f'* Contacts - Guest House GILE<{SMTP_USER}>'

        session.sendmail(SMTP_USER, staff_email_list, message.as_string())

    except Exception as ex:
        print(ex)
    finally:
        session.quit()


def send_client_notification_email(reservation):
    try:
        session = smtplib.SMTP('mail.gile.house', 25)
        session.starttls()
        session.login(SMTP_USER, SMTP_PASSWORD)
        name = reservation.cleaned_data['name']
        email_tmp = reservation.cleaned_data['email']
        check_in = reservation.cleaned_data['check_in'].date().strftime("%d.%m.%Y")
        check_out = reservation.cleaned_data['check_out'].date().strftime("%d.%m.%Y")

        msg = f"""Здравейте, {name},
Получихме заявката Ви за резервация от {check_in} до {check_out}. 
Този имейл се генерира автоматично и не означава, че престоят Ви е потвърден. Наш служител ще се свърже с вас или ще получите имейл за потвържение.
За контакт с нас: +359 88 560 3446, guest@gile.house или на бързата ни форма в сайта.

Hi, {name},
We received your reservation request from {check_in} to {check_out}.
This email is generated automatically and does not mean that your stay has been confirmed. A member of our staff will contact you or you will receive a confirmation email.
To contact us: +359 88 560 3446, guest@gile.house or fill the contact form on our website.
"""
        message = MIMEText(msg, 'plain')
        message['Subject'] = f'Получена заявка за резервация/ Received reservation request'
        message['From'] = f'Guest House GILE<{SMTP_USER}>'
        session.sendmail(SMTP_USER, email_tmp, message.as_string())
    except Exception as ex:
        print(ex)
    finally:
        session.quit()