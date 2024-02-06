from hotel_gile.settings import ADMIN_LIST_DISPLAY_DATETIME_FORMAT, ADMIN_LIST_DISPLAY_DATE_FORMAT, STATIC_URL, CURRENCY_DISPLAY
import hotel_gile.main_app.functions.auxiliary_functions as af
from hotel_gile.main_app.models.enums import ReservationStatus
import hotel_gile.main_app.validators as validators
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
from django.contrib import admin
from .models_rooms import Room
from django.db import models
import locale


class Reservation(models.Model):
    # Technical fields
    id = models.AutoField(primary_key=True, verbose_name="Резервация №")
    status = models.CharField(max_length=1, default=ReservationStatus.PENDING, choices=ReservationStatus.choices, verbose_name="Статус")
    added_on = models.DateTimeField(verbose_name='Резервирана на', blank=True, default=datetime.now)
    external_id = models.CharField(max_length=32, blank=True, null=True)
    email_sent = models.BooleanField(default=False)
    locker_password_id = models.CharField(max_length=30, blank=True, null=True)

    # Business fields
    name = models.CharField(max_length=150, verbose_name="Имена")
    phone = models.CharField(max_length=25, verbose_name="Телефон за връзка")
    email = models.EmailField(blank=True, null=True, verbose_name="Имейл")
    generate_password = models.BooleanField(default=False, verbose_name="Генерирай парола за достъп")
    check_in = models.DateTimeField(verbose_name="Настаняване", default=af.default_check_in, help_text="Ако няма час на пристигане остави 14:00")
    check_out = models.DateTimeField(verbose_name="Напускане", default=af.default_check_out)
    description = models.TextField(verbose_name='Коментар', blank=True, null=True)

    @property
    def get_locker_password(self):
        return str(int(self.added_on.timestamp() / 10000))

    @property
    def stay(self):
        return abs(self.check_in.date() - self.check_out.date()).days
    stay.fget.short_description = 'Нощувки'

    @property
    def title(self):
        inline_rooms = ReservedRooms.objects.filter(reservation=self).exclude(room__isnull=True).order_by('room')
        if len(inline_rooms) == 1:
            return f'Стая №{inline_rooms[0].room_id}'
        elif len(inline_rooms) > 1:
            return f'Стаи №: ' + ','.join([str(inline.room.id) for inline in inline_rooms])
        return f'Нова Резервация'
    title.fget.short_description = "Резервация"

    @property
    def price(self):
        inline_rooms = ReservedRooms.objects.select_related('reservation').filter(reservation=self)
        total_reservation_price = 0
        for inline in inline_rooms:
            if inline.room:
                total_reservation_price += inline.price_per_night * self.stay
        return total_reservation_price

    @property
    def price_currency(self):
        return f"{self.price:.2f} " + CURRENCY_DISPLAY
    price_currency.fget.short_description = "Крайна цена"

    # ADMIN FIELDS
    @admin.display(description="Резервация")
    def title_admin(self):
        return mark_safe(f'<img src="/{STATIC_URL}css/images/{self.status}.png" '
                         f'width="16" alt="Няма снимка" '
                         f'style="margin-right: 10px;vertical-align: middle;margin-top: -4px;"/>{self.title}')

    @admin.display(description="Име")
    def name_admin(self):
        return self.name.title()

    @admin.display(description="Настаняване")
    def check_in_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_in = self.check_in
        return check_in.strftime(ADMIN_LIST_DISPLAY_DATE_FORMAT)

    @admin.display(description="Напускане")
    def check_out_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_out = self.check_out
        return check_out.strftime(ADMIN_LIST_DISPLAY_DATE_FORMAT)

    @admin.display(description="Резервирана")
    def added_on_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        added_on = self.added_on
        return added_on.strftime(ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @classmethod
    def get_all_free_rooms(cls, check_in, check_out, reservation_id):
        check_in = check_in.replace(hour=0, minute=0)
        busy_rooms = ReservedRooms.objects.values_list('room', flat=True).exclude(
            reservation__id=reservation_id) \
            .exclude(room__isnull=True).filter(
            (models.Q(reservation__check_in__range=(check_in, check_out)))
            | (models.Q(reservation__check_out__range=(check_in + timedelta(days=1), check_out)))
            | (models.Q(reservation__check_in__lt=check_in, reservation__check_out__gt=check_out))).distinct()
        free_rooms = Room.objects.exclude(id__in=busy_rooms).all()
        return free_rooms

    def clean(self):
        validators.validate_reservation(self)
        self.name = self.name.lower()

    # def calculate_days(self):
    #     return abs(self.check_in.date() - self.check_out.date()).days

    class Meta:
        verbose_name = "Резервация"
        verbose_name_plural = "1. Резервации"

    def __str__(self):
        return "Резервация за " + self.title


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
    def calculate_price(cls, check_in, check_out, room, adults, children, discount):
        tmp_reservation = Reservation(check_in=check_in, check_out=check_out)
        tmp = ReservedRooms(reservation=tmp_reservation, room=room, adults=adults, children=children, discount=discount)

        return tmp.price_per_night, tmp.total_price

    @property
    def total_guests(self):
        children = self.clean_children()
        return self.adults + children

    @property
    def total_price(self):
        return self.stay * self.price_per_night

    @property
    def stay(self):
        return self.reservation.stay

    @property
    def title(self):
        return "Стая №" + str(self.room.id)

    @property
    def price_per_night(self):
        discount = self.clean_discount()
        price = self.room.price_per_night(self.total_guests, self.reservation.added_on) + discount
        if price:
            return price
        return 0

    @admin.display(description="Цена за нощувка")
    def admin_price_per_night(self):
        return f"{self.price_per_night:.2f} " + CURRENCY_DISPLAY

    @admin.display(description="Обща цена")
    def admin_total_price(self):
        return f"{self.total_price:.2f} " + CURRENCY_DISPLAY

    def clean_children(self):
        if not self.children:
            return 0
        return self.children

    def clean_discount(self):
        if not self.discount:
            return 0
        return self.discount

    def clean(self):
        validators.validate_reserved_rooms(self)

    def is_room_free(self, reservation_id):
        free_rooms = Reservation.get_all_free_rooms(self.reservation.check_in, self.reservation.check_out, reservation_id)
        if self.room in free_rooms:
            return True
        return False

    class Meta:
        verbose_name = "стая"
        verbose_name_plural = "стаи"
        unique_together = (("reservation", "room"),)

    def __str__(self):
        return f"№{self.room.id}" if self.room else "Няма избрана стая"
