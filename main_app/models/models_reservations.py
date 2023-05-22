import locale
from django.db import models
from datetime import datetime
from django.contrib import admin
from django.utils.safestring import mark_safe
import hotel_gile.main_app.validators as validators
import hotel_gile.main_app.auxiliary_functions as af
from hotel_gile.settings import ADMIN_LIST_DISPLAY_DATETIME_FORMAT, ADMIN_LIST_DISPLAY_DATE_FORMAT, STATIC_URL
from hotel_gile.main_app.technical_functions.technical_functions import get_all_free_rooms
from .models_rooms import Room


BOOL_CHOICES = ((True, 'Да'), (False, 'Не'))
RESERVATION_STATUSES = ((0, 'Заявена'), (1, 'Потвърдена'), (2, 'Платена'))
CURRENCY_DISPLAY = "лв."
CURRENCY = "BGN"


class Reservation(models.Model):
    # Technical fields
    id = models.AutoField(primary_key=True, verbose_name="Резервация №")
    status = models.IntegerField(default=0, choices=RESERVATION_STATUSES, verbose_name="Статус")
    added_on = models.DateTimeField(verbose_name='Резервирана на', blank=True, default=datetime.now)
    external_id = models.CharField(max_length=32, unique=True, blank=True, null=True)
    email_sent = models.BooleanField(default=False)

    # Business fields
    name = models.CharField(max_length=150, verbose_name="Имена")
    phone = models.CharField(max_length=25, verbose_name="Телефон за връзка")
    email = models.EmailField(blank=True, null=True, verbose_name="Имейл")
    check_in = models.DateTimeField(verbose_name="Настаняване", default=af.default_check_in, help_text="Ако няма час на пристигане остави 14:00")
    check_out = models.DateTimeField(verbose_name="Напускане", default=af.default_check_out)
    description = models.TextField(verbose_name='Коментар', blank=True, null=True)

    @property
    def calc_days(self):
        return self.calculate_days()
    calc_days.fget.short_description = 'Нощувки'

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
                total_reservation_price += inline.price_per_night * self.calc_days
        return total_reservation_price

    @property
    def price_currency(self):
        return f"{self.price:.2f} " + CURRENCY_DISPLAY
    price_currency.fget.short_description = "Крайна цена"

    @admin.display(description="Резервация")
    def title_admin(self):
        return mark_safe(f'<img src="/{STATIC_URL}css/images/{self.status}.png" '
                         f'width="16" alt="Няма снимка" '
                         f'style="margin-right: 10px;vertical-align: middle;margin-top: -4px;"/>{self.title}')

    @admin.display(description="Настаняване")
    def check_in_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_in = self.check_in
        return check_in.strftime(ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @admin.display(description="Име")
    def name_admin(self):
        return self.name.title()

    @admin.display(description="Резервирана")
    def added_on_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        added_on = self.added_on
        return added_on.strftime(ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @admin.display(description="Напускане")
    def check_out_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_out = self.check_out
        return check_out.strftime(ADMIN_LIST_DISPLAY_DATE_FORMAT)

    def clean(self):
        validators.validate_dates(self)
        self.name = self.name.lower()

    def calculate_days(self):
        return abs(self.check_in.date() - self.check_out.date()).days

    class Meta:
        verbose_name = "Резервация"
        verbose_name_plural = "1. Резервации"

    def __str__(self):
        return "Резервация за " + self.title


class ArchivedReservation(Reservation):
    class Meta:
        proxy = True
        verbose_name = "Архивирана резервация"
        verbose_name_plural = "9. Архивирани резервации"


class ReservedRooms(models.Model):
    reservation = models.ForeignKey(Reservation, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name="Стая", blank=True, null=True, on_delete=models.SET_NULL)
    adults = models.PositiveIntegerField(verbose_name="Брой възрастни", default=0)
    children = models.PositiveIntegerField(verbose_name="Брой деца", blank=True, null=True, default=0)
    discount = models.FloatField(verbose_name='Отстъпка/ Надценка', blank=True, null=True)
    price = models.FloatField(verbose_name='Цена', blank=True, null=True, default=0)

    @property
    def total_guests(self):
        children = self.clean_children()
        return self.adults + children

    @property
    def total_price(self):
        return self.stay * self.price_per_night

    @property
    def stay(self):
        return self.reservation.calculate_days()

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
        if self.room:
            validators.guests_exist(self)
            if self.is_room_busy(self.reservation.id):
                validators.room_is_busy(self.room.id)
            validators.is_room_capacity_exceeded(self)
            self.price = self.total_price
        else:
            if self.reservation.status > 0:
                validators.room_is_not_chosen()
            self.price = 0

    def is_room_busy(self, reservation_id):
        free_rooms = get_all_free_rooms(self.reservation.check_in, self.reservation.check_out, reservation_id, reservedrooms=ReservedRooms, room=Room)
        if self.room in free_rooms:
            return False
        return True

    class Meta:
        verbose_name = "стая"
        verbose_name_plural = "стаи"
        unique_together = (("reservation", "room"),)

    def __str__(self):
        return f"№{self.room.id}" if self.room else "Няма избрана стая"

