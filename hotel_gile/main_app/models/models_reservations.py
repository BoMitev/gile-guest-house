from hotel_gile.main_app.services import asi_tuya, asi_payments, asi_google, asi_email
from hotel_gile.main_app.functions import auxiliary_func as af
from ..models.models_rooms import Room
from ..models.enums import ReservationStatus
import hotel_gile.main_app.validators as validators
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
import hotel_gile.settings as settings
from django.utils import timezone
from django.contrib import admin
from django.db import models
import locale


class Reservation(models.Model):
    # Technical fields
    id = models.AutoField(primary_key=True,
                          verbose_name="Резервация №")
    status = models.CharField(max_length=1,
                              default=ReservationStatus.PENDING,
                              choices=ReservationStatus.choices,
                              verbose_name="Статус")
    added_on = models.DateTimeField(verbose_name='Резервирана на',
                                    blank=True,
                                    default=datetime.now)
    external_id = models.CharField(max_length=32,
                                   blank=True,
                                   null=True)
    email_sent = models.BooleanField(default=False)
    locker_password_id = models.CharField(max_length=30,
                                          blank=True,
                                          null=True)
    payment_id = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    payment_counter = models.IntegerField(default=0)

    # Business fields
    name = models.CharField(max_length=150, verbose_name="Имена")
    phone = models.CharField(max_length=25, verbose_name="Телефон за връзка")
    email = models.EmailField(blank=True, null=True, verbose_name="Имейл")
    generate_password = models.BooleanField(default=False, verbose_name="Генерирай парола за достъп")
    check_in = models.DateTimeField(verbose_name="Настаняване", default=af.default_check_in,
                                    help_text="Ако няма час на пристигане остави 14:00")
    check_out = models.DateTimeField(verbose_name="Напускане", default=af.default_check_out)
    description = models.TextField(verbose_name='Коментар', blank=True, null=True)

    def __str__(self):
        return "Резервация за " + self.title

    class Meta:
        verbose_name = "Резервация"
        verbose_name_plural = "1. Резервации"

    @classmethod
    def get_all_free_rooms(cls, check_in, check_out, reservation_id):
        check_in = check_in.replace(hour=0, minute=0)
        check_out = check_out.replace(hour=0, minute=0)
        busy_rooms = ReservedRooms.objects.values_list('room', flat=True).exclude(
            reservation__id=reservation_id) \
            .exclude(room__isnull=True).filter(
            (models.Q(reservation__check_in__range=(check_in, check_out)))
            | (models.Q(reservation__check_out__range=(check_in + timedelta(days=1), check_out)))
            | (models.Q(reservation__check_in__lt=check_in, reservation__check_out__gt=check_out))).distinct()
        free_rooms = Room.objects.exclude(id__in=busy_rooms).all()
        return free_rooms

    @staticmethod
    def unlink_reservations(reservations):
        for reservation in reservations:
            if reservation.external_id:
                try:
                    asi_google.delete_reservation(reservation)
                except Exception as ex:
                    print(ex)

    @property
    def locker_password(self):
        return int(self.added_on.timestamp() / 10000)

    @property
    def payment_url(self):
        if self.payment_id:
            return f"{settings.PAYMENT_URL}/merchants/ecom/payment.html?mdOrder={self.payment_id}&language={self.is_owner_bg()}"
        return ""

    @property
    def stay(self):
        return (self.check_out.date() - self.check_in.date()).days

    stay.fget.short_description = 'Нощувки'

    @property
    def price(self):
        total_reservation_price = 0
        for inline in self.reservedrooms_set.all():
            if inline.room:
                total_reservation_price += inline.price_per_night * self.stay
        return total_reservation_price

    @property
    def title(self):
        rooms = self.reservedrooms_set.values_list('room_id', flat=True)
        if rooms[0] is None:
            return f'Нова Резервация'
        if len(rooms) > 1:
            return f'Стаи №: ' + ','.join([str(x) for x in rooms])
        return f'Стая №{rooms[0]}'

    title.fget.short_description = "Резервация"

    def is_owner_bg(self):
        if af.has_cyrillic(self.name):
            return "bg"
        return "en"

    def clean(self):
        validators.validate_reservation(self)
        self.name = self.name.lower()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        has_changed = kwargs.get('has_changed', False)
        if has_changed is True:
            if self.status == ReservationStatus.PENDING:
                self.unlink_reservations([self])
            else:
                related_rooms = self.reservedrooms_set.all()

                asi_google.send_update_reservation(self, related_rooms)

                if self.generate_password is True:
                    asi_tuya.create_tuya_password(self)

                if self.email_sent is False and self.email:
                    if not self.payment_id:
                        asi_payments.generate_payment_link(self)

                    asi_email.send_confirmation_email(self, related_rooms)

            if self.generate_password is False:
                asi_tuya.delete_tuya_password(self)
        return super().save(force_insert, force_update, using, update_fields)

    # ADMIN FIELDS
    @admin.display(description="Крайна цена")
    def price_currency(self):
        return f"{self.price: .2f} " + settings.CURRENCY_DISPLAY

    @admin.display(description="Резервация")
    def title_admin(self):
        return mark_safe(f'<img src="/{settings.STATIC_URL}css/images/{self.status}.png" '
                         f'width="16" alt="Няма снимка" '
                         f'style="margin-right: 10px;vertical-align: middle;margin-top: -4px;"/>{self.title}')

    @admin.display(description="Име")
    def name_admin(self):
        return self.name.title()

    @admin.display(description="Настаняване")
    def check_in_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_in = self.check_in
        return check_in.strftime(settings.ADMIN_LIST_DISPLAY_DATE_FORMAT)

    @admin.display(description="Напускане")
    def check_out_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_out = self.check_out
        return check_out.strftime(settings.ADMIN_LIST_DISPLAY_DATE_FORMAT)

    @admin.display(description="Резервирана")
    def added_on_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        added_on = self.added_on
        return added_on.strftime(settings.ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @admin.display(description="Телефон за връзка")
    def phone_link(self):
        return mark_safe(f"<a href='tel:{self.phone}'>{self.phone}</a>")

    @admin.display(description="Имейл")
    def email_link(self):
        if self.email:
            return mark_safe(f"<a href='mailto:{self.email}'>{self.email}</a>")
        return "-"


class ArchivedReservation(Reservation):
    class Meta:
        proxy = True
        verbose_name = "Архивирана резервация"
        verbose_name_plural = "8. Архивирани резервации"


class ReservedRooms(models.Model):
    reservation = models.ForeignKey(Reservation, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name="Стая", blank=True, null=True, on_delete=models.SET_NULL)
    adults = models.PositiveIntegerField(verbose_name="Брой възрастни", default=0)
    children = models.PositiveIntegerField(verbose_name="Брой деца", default=0)
    discount = models.FloatField(verbose_name='Отстъпка/ Надценка', blank=True, null=True)
    price = models.FloatField(verbose_name='Цена', blank=True, null=True, default=0)

    @classmethod
    def calculate_price(cls, reservation_id, check_in, check_out, room, adults, children, discount):
        reservation = Reservation.objects.filter(id=reservation_id)
        added_on = datetime.now()

        if reservation.exists():
            reservation = reservation.first()
            added_on = reservation.added_on

        reservation = Reservation(check_in=check_in, check_out=check_out, added_on=added_on)
        rooms = cls(reservation=reservation, room=room, adults=adults, children=children, discount=discount)
        return rooms.price_per_night, rooms.total_price

    @property
    def total_guests(self):
        children = self.clean_children()
        return self.adults + children

    @property
    def total_price(self):
        return self.reservation.stay * self.price_per_night

    @property
    def title(self):
        return "Стая №" + str(self.room.id)

    @property
    def price_per_night(self):
        discount = self.clean_discount()
        price = self.room.price_per_night(self.total_guests, self.reservation.added_on) + discount
        return price if price else 0

    @admin.display(description="Цена за нощувка")
    def admin_price_per_night(self):
        return f"{self.price_per_night:.2f} " + settings.CURRENCY_DISPLAY

    @admin.display(description="Обща цена")
    def admin_total_price(self):
        return f"{self.total_price:.2f} " + settings.CURRENCY_DISPLAY

    def clean_children(self):
        return self.children if self.children else 0

    def clean_discount(self):
        return self.discount if self.discount else 0

    def clean(self):
        validators.validate_reserved_rooms(self)

    def is_room_free(self, reservation_id):
        free_rooms = Reservation.get_all_free_rooms(self.reservation.check_in, self.reservation.check_out,
                                                    reservation_id)
        return True if self.room in free_rooms else False

    class Meta:
        verbose_name = "стая"
        verbose_name_plural = "стаи"
        unique_together = (("reservation", "room"),)

    def __str__(self):
        return f"№{self.room.id}" if self.room else "Няма избрана стая"


class PaymentLogs(models.Model):
    host = models.CharField(max_length=150)
    method = models.CharField(max_length=7)
    request_body = models.JSONField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    code = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def reservation_id(self):
        order_number = self.request_body.get('orderNumber', None)
        if order_number:
            return order_number.split("-")[0]
        return "Unknown"

    reservation_id.fget.short_description = "Резервация"

    @property
    def reservation(self):
        return Reservation.objects.filter(pk=self.reservation_id).first()

    @property
    def reservation_url(self):
        from django.urls import reverse
        obj = self.reservation
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=(obj.id,))
        return mark_safe(f'<a href="{url}">{obj}</a>')

    reservation_url.fget.short_description = "Резервация"

    class Meta:
        verbose_name = "Банков лог"
        verbose_name_plural = "9. Банкови логове"

    def __str__(self):
        return f"{self.method} - {self.code}"
