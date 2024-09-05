from django.template.loader import render_to_string
from hotel_gile.settings import ALTERNATIVE_USER
from ..email_srvc import send_email


def send_confirmation_email(reservation, all_rooms):
    subject = f'Потвърдена резервация №{reservation.id}/ Confirmed reservation №{reservation.id}'
    context = {
        'reservation': reservation,
        'check_in': reservation.check_in.date().strftime("%d.%m.%Y"),
        'check_out': reservation.check_out.date().strftime("%d.%m.%Y"),
        'all_rooms': all_rooms,
        'room_list': ', '.join(["№" + str(x.room.id) for x in all_rooms]),
        'has_password': True if reservation.locker_password_id else False,
        'person_count': sum([(room.adults + room.children) for room in all_rooms]),
        'price_per_night': reservation.price / reservation.stay
    }
    body_html = render_to_string('email_templates/reservation_confirm_email.html', context)
    recipient_list = [reservation.email, ALTERNATIVE_USER]
    payload = {
        'subject': subject,
        'emails': recipient_list,
        'body': body_html
    }

    response = send_email(payload)
    if response.status_code == 200:
        reservation.email_sent = True
        return True
    return False


def send_reject_email(reservation):
    subject = f'Отхвърлена резервация/ Services unavailable'
    context = {
        'reservation': reservation,
        'check_in': reservation.check_in.date().strftime("%d.%m.%Y")
    }
    body_html = render_to_string('email_templates/reservation_rejection_email.html', context)
    payload = {
        'subject': subject,
        'emails': [reservation.email],
        'body': body_html
    }

    send_email(payload)


def send_notification_email(event):
    from hotel_gile.main_app.forms import ContactForm, ReservationForm
    from django.contrib.auth.models import User

    staff_email_list = [x[0] for x in User.objects.filter(is_staff=True).values_list('email') if x[0]]
    if not staff_email_list:
        return

    subject, body = "", ""
    name = event.cleaned_data['name'].title()

    if isinstance(event, ReservationForm):
        total_guests_count = event.cleaned_data['adults'] + event.cleaned_data['children']
        rooms_count = event.cleaned_data['rooms']
        check_in = event.cleaned_data['check_in'].date().strftime('%d.%m.%Y')
        check_out = event.cleaned_data['check_out'].date().strftime('%d.%m.%Y')
        stay = abs(event.cleaned_data['check_in'].date() - event.cleaned_data['check_out'].date()).days
        phone = event.cleaned_data['phone']

        subject = "Нова резервация"
        body = f"Получихте нова резервация. <br>" \
               f"Име: {name} <br>" \
               f"Брой гости: {total_guests_count} <br>" \
               f"Брой стаи: {rooms_count} <br>" \
               f"От: {check_in} <br>" \
               f"До: {check_out} <br>" \
               f"Нощувки: {stay} <br>" \
               f"Телефон: {phone}"
    elif isinstance(event, ContactForm):
        email = event.cleaned_data['email']
        message = event.cleaned_data['message']

        subject = "Ново запитване"
        body = f"Получихте ново запитване. <br>" \
               f"Име: {name} <br>" \
               f"Имейл: {email} <br>" \
               f"Запитване: {message}"
    payload = {
        'subject': subject,
        'emails': staff_email_list,
        'body': body
    }

    send_email(payload)


def send_client_notification_email(reservation):
    name = reservation.cleaned_data['name']
    email = reservation.cleaned_data['email']
    check_in = reservation.cleaned_data['check_in'].date().strftime("%d.%m.%Y")
    check_out = reservation.cleaned_data['check_out'].date().strftime("%d.%m.%Y")

    subject = "Получена заявка за резервация/ Received reservation request"
    body = f"Здравейте, {name},<br>" \
           f"Получихме заявката Ви за резервация от {check_in} до {check_out}.<br>" \
           f"Този имейл се генерира автоматично и не означава, че престоят Ви е потвърден. Наш служител ще се свърже с вас или ще получите имейл за потвържение.<br>" \
           f"За контакт с нас: +359 88 560 3446, guest@gile.house или на бързата ни форма в сайта. <br>" \
           f"<br>" \
           f"Hi, {name},<br>" \
           f"We received your reservation request from {check_in} to {check_out}.<br>" \
           f"This email is generated automatically and does not mean that your stay has been confirmed. A member of our staff will contact you or you will receive a confirmation email.<br>" \
           f"To contact us: +359 88 560 3446, guest@gile.house or fill the contact form on our website."

    payload = {
        'subject': subject,
        'emails': [email],
        'body': body
    }
    send_email(payload)


def send_successful_payment_email(reservation):
    from hotel_gile.main_app.functions.auxiliary_func import has_cyrillic
    from hotel_gile.main_app.models import TermWorkListCol

    if has_cyrillic(reservation.name):
        contacts = TermWorkListCol.objects.filter(link__language="bg", column_ident="footer_contacts").first()
        subject = "Вашето плащане беше успешно"
        context = {
            "title": f"Благодарим Ви, {reservation.name.title()}",
            "body": f"Плащането е извършено успешно. <br>Резервация <b>№{reservation.id}</b>",
            "contact_us": "Ако имате въпроси или притеснения, моля, не се колебайте да ме уведомите.",
            "click_here": "Тук",
            "contacts": contacts.column_description,
            "rights": "&copy; 2024 Всички права запазени"
        }
    else:
        contacts = TermWorkListCol.objects.filter(link__language="en", column_ident="footer_contacts").first()
        subject = "Your payment was successful"
        context = {
            "title": f"Thanks, {reservation.name.title()}",
            "body": f"The payment has been done successfully. <br>Reservation <b>№{reservation.id}</b> ",
            "contact_us": "If you have any questions or concerns, feel free to get in touch.",
            "click_here": "Click here",
            "contacts": contacts.column_description,
            "rights": "&copy; 2024 All Rights Reserved"
        }

    body_html = render_to_string('email_templates/reservation_successful_payment.html', context)
    payload = {
        'subject': subject,
        'emails': [reservation.email],
        'body': body_html
    }
    send_email(payload)

